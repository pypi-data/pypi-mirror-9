#!/usr/bin/env python2.7

import boto.utils
import boto.ec2
import boto.iam
import datetime
import os
import os.path
import sys
import argparse
import yaml
import StringIO
import re
import time
import textwrap
import string

class Config(dict):
    def __init__(self):
        try:
            if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yaml")):
                cfg = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yaml"), 'r')
            elif os.path.isfile("/etc/provision-ec2.yaml"):
                cfg = open("/etc/provision-ec2.yaml")
            else:
                raise IOError("missing config file")
            self.update(yaml.safe_load(cfg.read()))
            cfg.close()
        except IOError, e:
            print("Config file error\n")
            print(e)
            sys.exit(1)
        except yaml.YAMLError, e:
            print("Config file error\n")
            print(e)
            sys.exit(1)

def ec2_iam_authenticate(region="us-east-1"):
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    security_token = os.environ.get("AWS_SECURITY_TOKEN")

    try:
        ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        st = False
    except:
        try:
            ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=security_token)
            st = True
        except:
            print """Invalid or missing AWS credentials in environment.
Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY. Optional: AWS_SECURITY_TOKEN.
See https://metamarkets.atlassian.net/wiki/display/OP/Provisioning+EC2"""
            sys.exit(1)

    return ec2

def iam_iam_authenticate(region="us-east-1"):
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    security_token = os.environ.get("AWS_SECURITY_TOKEN")

    try:
        iam = boto.iam.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        st = False
    except:
        try:
            iam = boto.iam.connect_to_region(region, aws_access_key_id=access_key, aws_secret_access_key=secret_key, security_token=security_token)
            st = True
	except:
            print """Invalid or missing AWS credentials in environment.
Required: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY. Optional: AWS_SECURITY_TOKEN.
See https://metamarkets.atlassian.net/wiki/display/OP/Provisioning+EC2"""
            sys.exit(1)

    return iam

def parse(possibilities):
    parser = argparse.ArgumentParser(description=textwrap.fill("Provision and tag EC2 instances for Metamarkets services."),
            epilog=textwrap.dedent('''\
    If the instance is tagged with galaxy_env, galaxy_version, and galaxy_type, then it will
    automatically get a Name tag, galaxy assigned, and the service will be started. If any of
    -e, -v, or -t options are used, then ALL are required. E.g.

    %(prog)s -e druid -v "2013-12-06T18:21:10Z" -t "prod/compute/hot" cr1.8xlarge 1 us-east-1a

    If the galaxy tags are not used, then --name, --info, and --env are required.

    Instance IAM roles will be assigned automatically with the name "service-ENV".
    The role name can be overridden with the --iam-instance-profile option.

    Required environment variables:
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_SECURITY_TOKEN (Only for temporary credentials)'''),
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('instancetype', metavar="TYPE", help="Instance type")
    parser.add_argument('count', metavar="N", help="Number of instances")
    parser.add_argument('az', metavar="AZ", choices=possibilities["AZ"], help="Availability Zone")
    parser.add_argument('-e', '--galaxy_env', metavar="ENV", help="Set the galaxy_env tag for self assignment.")
    parser.add_argument('-v', '--galaxy_version', metavar="VERSION", help="Set the galaxy_version tag for self assignment.")
    parser.add_argument('-t', '--galaxy_type', metavar="TYPE", help="Set the galaxy_type tag for self assignment.")
    parser.add_argument('-n', '--name', metavar="NAME", help="Prefix for the Name tag. The instance id will be appended with a '-' as a separator. This is automatically generated from the galaxy tags, but this option overrides that.")
    parser.add_argument('-i', '--info', metavar="DESCRIPTION", help="The purpose of the instance.")
    parser.add_argument('-E', '--env', metavar="ENV", help="The environment tag: 'prod' or 'not prod'.", choices=['prod', 'not prod'])
    parser.add_argument('-r', '--iam-instance-profile', metavar="ROLE", help="IAM role to assign to the instance. If this option is not given, then a default role name based on the galaxy_env option is used.", choices=possibilities["instance-profile"], default=None)
    parser.add_argument('--iam-instance-profile-arn', metavar="ARN", help="ARN for IAM Instance Profile to assign to the instance. This overrides the -r option.", default=None)
    parser.add_argument('--bid-price', metavar="PRICE", type=float, help="Request spot instances at this bid price.")
    parser.add_argument('--hugepages', metavar="HUGEPAGES", type=int, help="Set number of hugepages.", default=None)
    parser.add_argument('--disable-hyperthreading', help="Disable hyperthreading.", action='store_false', dest='hyperthreading')
    parser.add_argument('--java', metavar="JAVA", help="Override default Java version.")
    parser.add_argument('--tag', metavar="Key=NAME,Value=VALUE",
                        help="Tags to create.",
                        action="append")
    args = parser.parse_args()

    if (((args.galaxy_env is None) or
         (args.galaxy_version is None) or
         (args.galaxy_type is None)) and
        not ((args.galaxy_env is None) and
             (args.galaxy_version is None) and
             (args.galaxy_type is None))):
        print("error: Must have either all galaxy related tags or none.")
        sys.exit(1)
    if args.tag is not None:
        for tag in args.tag:
            if not re.match(r'^Key=.*,Value=.*$', tag):
                print("error: invalid tag: {0}".format(tag))
                parser.print_help()
                sys.exit(1)

    if (((args.galaxy_env is None) and
         (args.galaxy_version is None) and
         (args.galaxy_type is None)) and
         (args.name is None or args.info is None or args.env is None)):
        print("error: Please specify all of the galaxy tags: -e app -v version -t type")
        print("       Or name, info, and env: -n name -i info -E <prod or not prod>")
        sys.exit(1)

    return args

def get_possibilities(config):
    possibilities  = {}
    possibilities["AZ"] = []
    possibilities["instance-profile"] = []
    for region in config['regions']:
        ec2 = ec2_iam_authenticate(region)
        for zone in ec2.get_all_zones():
            possibilities["AZ"].append(zone.name)
        iam = iam_iam_authenticate(region)
        response = iam.list_instance_profiles()
        for profile in response['list_instance_profiles_response']['list_instance_profiles_result']['instance_profiles']:
            possibilities["instance-profile"].append(profile['instance_profile_name'])

    return possibilities

def mk_ephemeral_bdmap(count):
    if count == 0:
        return None
    else:
        bdmap = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        for i in range(0,count):
            bdmap["/dev/sd" + chr(ord('b') + i)] = boto.ec2.blockdevicemapping.BlockDeviceType(ephemeral_name="ephemeral{0}".format(i) )
        return bdmap

def mkuserdata(config, args):
    ud = string.Template(config.get('userdata', {}).get('template', ''))
    mapping = config.get('userdata', {}).get('default', {})
    tags = {}
    tags['creator'] = os.environ.get('LOGNAME', '???')
    if args.tag is not None:
        for tag in args.tag:
            k = re.sub(r'^Key=(.*),Value=(.*)$', r'\1', tag)
            v = re.sub(r'^Key=(.*),Value=(.*)$', r'\2', tag)
            tags[k] = v
    if ((args.galaxy_env is not None) and
        (args.galaxy_version is not None) and
        (args.galaxy_type is not None)):
        mapping['galaxy_agent'] = "true"
        tags['galaxy_env'] = args.galaxy_env
        mapping['galaxy_environment'] = args.galaxy_env
        mapping['service'] = args.galaxy_env
        tags['galaxy_version'] = args.galaxy_version
        mapping['galaxy_version'] = args.galaxy_version
        tags['galaxy_type'] = args.galaxy_type
        mapping['galaxy_type'] = args.galaxy_type
        #replace '/' with '-' for hostname generation
        mapping['application'] = args.galaxy_type.replace('/', '-')
        if (("prod" in args.galaxy_type) or
            ("enterprise" in args.galaxy_type)):
            tags['environment'] = "prod"
        else:
            tags['environment'] = "not prod"
    if args.name is not None:
        mapping['hostname'] = args.name
    if args.info is not None:
        tags['info'] = args.info
    if args.env is not None:
        tags['environment'] = args.env
    if args.hyperthreading is not None:
        mapping['hyperthreading'] = args.hyperthreading
    if args.hugepages is not None:
        mapping['hugepages'] = args.hugepages
    if args.java is not None:
        mapping['java'] = args.java
    # Add options for the following
    #mnt_raid_level: raid0
    #ebs_raid_level: raid0
    #mnt_filesystem: xfs
    #ebs_filesystem: xfs
    #mnt_options: noatime,attr2
    #ebs_options: noatime,attr2,nobarrier
    #grains:

    #Set indent to 8 as kludge
    mapping['tags'] = yaml.dump({'tags': tags}, default_flow_style=False, indent=8)
    return ud.substitute(mapping)

def print_instance(instance, spot_bid_price):
    print("id: {0}".format(instance.id))
    print("state: {0}".format(instance.state))
    print("instance_type: {0}".format(instance.instance_type))
    print("placement: {0}".format(instance.placement))
    print("public_dns_name: {0}".format(instance.public_dns_name))
    print("ip_address: {0}".format(instance.ip_address))
    print("private_dns_name: {0}".format(instance.private_dns_name))
    print("private_ip_address: {0}".format(instance.private_ip_address))
    print("key_name: {0}".format(instance.key_name))
    print("launch_time: {0}".format(instance.launch_time))
    print("image_id: {0}".format(instance.image_id))
    print("virtualization_type: {0}".format(instance.virtualization_type))
    print("groups: {0}".format(instance.groups))
    print("Spot request id: {0}".format(instance.spot_instance_request_id))
    if spot_bid_price:
        print("Spot bid price: {0}".format(spot_bid_price))
    if instance.instance_profile:
        print("role: {0}".format(instance.instance_profile.items()))

if __name__ == "__main__":
    config = Config()
    possibilities = get_possibilities(config)
    args = parse(possibilities)
    region = args.az[0:-1]
    params = config['instance-type'].get(args.instancetype, config['instance-type']['default'])
    bdmap = mk_ephemeral_bdmap(params['ephemeralcount'])
    instance_profile_name = None
    if args.iam_instance_profile_arn is None:
        if args.iam_instance_profile is None:
            #search config for instance profile
            if args.galaxy_env is not None:
                if config['galaxy'].get(args.galaxy_env):
                    if config['galaxy'][args.galaxy_env].get('instance-profile'):
                        instance_profile_name = config['galaxy'][args.galaxy_env].get('instance-profile')
                    else:
                        for key in config['galaxy'][args.galaxy_env]:
                            if key in args.galaxy_type:
                                instance_profile_name = config['galaxy'][args.galaxy_env][key].get('instance-profile')
                                continue
        else:
            instance_profile_name = args.iam_instance_profile
        iam = iam_iam_authenticate(region)
        try:
            instance_profile = iam.get_instance_profile(instance_profile_name)['get_instance_profile_response']['get_instance_profile_result']['instance_profile']['arn']
        except StandardError, e:
            if instance_profile_name:
                print("Could not find instance profile named {0}".format(instance_profile_name))
                print(str(e))
                sys.exit(1)
            instance_profile = None
    else:
        instance_profile = args.iam_instance_profile_arn

    ec2 = ec2_iam_authenticate(region)
    if not args.bid_price:
        # Standard instance launch
        reservation = ec2.run_instances(config['AMIs'][region][params['type']],
                min_count=args.count, max_count=args.count,
                key_name=config['keypair'], security_groups=config['sg'],
                instance_type=args.instancetype, block_device_map=bdmap,
                placement=args.az, user_data=mkuserdata(config, args),
                instance_profile_arn=instance_profile)
        for instance in reservation.instances:
            instance.update()
            print("{id} {type} {az} {state}".format(id=instance.id, type=instance.instance_type, az=instance.placement, state=instance.state))
            print("\n")
        for instance in reservation.instances:
            while instance.state == "pending":
                time.sleep(1)
                instance.update()
            if instance.state == "running":
                tags = ec2.get_all_tags(filters={"resource-id": instance.id})
                print_instance(instance, None)
            else:
                print("{id} {state}".format(id=instance.id, state=instance.state))
    else:
        # Spot instance launch
        # TODO Can fail to cancel requests if they were already fulfilled when finally runs
        # TODO Can fail to cancel requests if the script dies without the finally working; kill -9, machine failure, network failure
        # TODO Can fail to assign tags before instance starts up due to polling race
        requests = ec2.request_spot_instances(args.bid_price, config['AMIs'][region][params['type']],
                count=args.count,
                type="one-time",
                key_name=config['keypair'], security_groups=config['sg'],
                instance_type=args.instancetype, block_device_map=bdmap,
                placement=args.az, user_data=mkuserdata(config, args),
                instance_profile_arn=instance_profile)
        request_ids = []
        for request in requests:
            request_ids.append(request.id)
        fulfilled_requests = {}
        try:
            n = 0
            while len(fulfilled_requests) != len(request_ids):
                time.sleep(2)
                # Don't want to spam the console.
                printable = n % 15 == 0
                n = n + 1
                if printable:
                    print "[" + str(datetime.datetime.now()) + "] waiting for: ",
                updated_requests = ec2.get_all_spot_instance_requests([id for id in request_ids if id not in fulfilled_requests])
                new_instances = []
                for updated_request in updated_requests:
                    if printable:
                        print "{0} ({1}{2}), ".format(updated_request.id, updated_request.status.code, (" " + updated_request.instance_id) if updated_request.instance_id else ""),
                    if updated_request.status.code == "fulfilled" and updated_request.instance_id and updated_request.id not in fulfilled_requests:
                        fulfilled_requests[updated_request.id.strip()] = True
                        new_instances.append(updated_request.instance_id)
                if printable:
                    print
                for instance_id in new_instances:
                    instances = ec2.get_only_instances([instance_id])
                    if len(instances) != 1:
                        raise Exception("wtf?! expected single instance when asking for: {0}".format(instance_id))
                    for instance in instances:
                        while instance.state == "pending":
                            time.sleep(1)
                            instance.update()
                        if instance.state == "running":
                            tags = ec2.get_all_tags(filters={"resource-id": instance.id})
                            print_instance(instance, args.bid_price)
                        else:
                            print("{id} {state}".format(id=instance.id, state=instance.state))
        finally:
            outstanding = [str(id) for id in request_ids if id not in fulfilled_requests]
            if outstanding:
                ec2.cancel_spot_instance_requests(outstanding)
                print "canceled outstanding requests: " + str(outstanding)
