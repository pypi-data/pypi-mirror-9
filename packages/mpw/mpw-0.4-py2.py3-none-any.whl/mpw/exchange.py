
def export(config, of, reveal_passwords):
    of.write('# Master Password site export\n')
    if reveal_passwords:
        of.write('#     Export of site names and passwords in clear-text.\n')
    else:
        of.write('#     Export of site names and stored passwords (unless device-private) encrypted with the master key.\n')
    of.write('# \n')
    of.write('##\n')
    of.write('# User Name: %s\n' % username)
    of.write('# Avatar: 0\n')
    of.write('# Key ID: %x\n' % key_id)
    of.write('# Date: %s\n' % date_rfc3339_format)
    of.write('# Version: %s\n' % program_version)
    of.write('# Format: 1\n')
    if reveal_passwords:
        of.write('# Passwords: VISIBLE\n')
    else:
        of.write('# Passwords: PROTECTED\n')
    of.write('##\n')
    of.write('# \n')
    of.write('#               Last     Times  Password                      Login\t                     Site\tSite\n')
    of.write('#               used      used      type                       name\t                     name\tpassword\n')

    for site in config:
        last_used = format_rfc3339(site['last_used'])
        uses = site['uses']
        type = sites['type']
        version = site['version']
        login_name = site['login_name']
        site_name = site['site_name']
        content = ''
        if site['is_generated']:
            counter = site['counter']
        if type and site['is_device_private']:
            if reveal_passwords:
                content = [site['algorithm'], get_pwd(site), site['key']]  # resolvePasswordForSite
            else:
                content = [site['algorithm'], export_pwd(site), site['key']]  # exportPasswordForSite

        of.write('%@ %8ld %8s %25s\t%25s\t%@\n' % (last_used, uses, '%lu, %lu, %lu' % (type, version, counter), username, sitename, content))
