import os
import time
from waflib.TaskGen import feature
import orch.features
import tarfile

# from https://github.com/brettviren/python-ups-utils
try:
    import ups.commands 
except ImportError:
    print 'Failed to import, do you need to install: https://github.com/brettviren/python-ups-utils'
    raise

def configure(cfg):
    orch.features.register_defaults(
        'upsinit',
        ups_products_dir = '',
        ups_version = '5.1.2',
    )
    orch.features.register_defaults(
        'upsprod',
        # must be set in config
        ups_products_dir = '',  

        # the UPS product name may differ from the package
        ups_product_name = '{package}',
        # some places like wonky version strings
        ups_product_version = 'v{version_underscore}',
        # where, under this subdir, is the table held
        ups_table_dir = 'ups', 
        # name of the table file
        ups_table_file = '{ups_product_name}.table',
        # the directory holding a UPS version file relative to ups_products_dir
        ups_version_subdir = '{ups_product_name}/{ups_product_version}.version',

        # ordered, colon-separated list of qualifier tags 
        ups_qualifiers = '',
        ups_quals_dashed = 'UPS_QUALS_DASHED',
        ups_quals_underscore = 'UPS_QUALS_UNDERSCORE',

        # if you set qualifiers you probably want to modify the following also

        # the UPS version file name
        ups_version_file = '{ups_flavor}{ups_quals_dashed}',

        # how to go from products directory to where the product's files are actually installed. 
        ups_product_subdir = '{ups_product_name}/{ups_product_version}/{ups_flavor}{ups_quals_underscore}',

        # who to name the UPS tarball package
        ups_tarball_package = '{ups_product_name}-{version}-{ups_flavor}{ups_quals_dashed}.tar.bz2'

    )
    return
        

# tool interface
def build(bld):
    pass


def monkey_worch(w):
    'Evil monkey massage to set dependent variables to a functional default'
    qd = w.ups_qualifiers.replace(':','-') or ''
    if qd:
        qd = '-' + qd
    qu = w.ups_qualifiers.replace(':','_')
    qu = '_' + qu               # always leading underscore

    for k,v in w._config.items():
        newv = v.replace('UPS_QUALS_DASHED',qd).replace('UPS_QUALS_UNDERSCORE',qu)
        #print '%s: "%s" "%s" "%s" -> "%s"' % (k, qd,qu,v,newv)
        if v == newv:
            continue
        w._config[k] = newv
    return w


@feature('upsinit')
def feature_upsinit(tgen):
    '''
    Initialize a UPS products area including installing a UPS package.
    '''
    #w = monkey_worch(tgen.worch)
    w = tgen.worch

    products_dir = tgen.make_node(w.ups_products_dir)
    setups_file = products_dir.make_node('setups')

    def upsinit(task):
        ups.commands.install(w.ups_version, products_dir.abspath())

    tgen.step('upsinit', 
              rule = upsinit, 
              update_outputs = True,
              target = setups_file)

    def upspack(task):
        tf = tarfile.open(task.outputs[0].abspath(), mode='w:bz2')
        for thing in ['setup', 'setups', 'setups_layout', 'ups', '.upsfiles']:
            tf.add(os.path.join(products_dir.abspath(), thing),
                   arcname = thing, recursive = True)

    tgen.step('upspack',
              rule = upspack,
              source  = setups_file,
              target = w.format('upspack/ups-{ups_version}-{ups_flavor}.tar.bz2'))

    pass

# /bin/bash -c 'source `pwd`/setups && ups declare hello v2_8 -f "Linux64bit+3.13-2.19" -r hello/v2_8 -m hello.table -M Linux64bit+3.13-2.19/ups'
# 

@feature('upsprod')
def feature_upsprod(tgen):
    '''
    Produce a UPS product's table and version files.
    '''
    w = monkey_worch(tgen.worch)

    assert w.ups_products_dir
    assert w.ups_product_subdir

    idir = tgen.make_node(w.install_dir)

    repo = tgen.make_node(w.ups_products_dir)
    pdir = repo.make_node(w.ups_product_subdir)
    tdir = pdir.make_node(w.ups_table_dir)
    table_node = tdir.make_node(w.ups_table_file)

    vdir = repo.make_node(w.ups_version_subdir)
    version_node = vdir.make_node(w.ups_version_file)

    def wash_path(path, fromnode, noparent = True):
        'Turn absolute paths into ones relative to fromnode'
        if not path.startswith('/'):
            return 
        pnode = tgen.make_node(path)
        rel = pnode.path_from(fromnode)
        if rel.startswith('..') and noparent:
            return 
        return rel

    def upstable(task):
        preamble = w.format('''\
File    = table
Product = {ups_product_name}
Group:
  Flavor = {ups_flavor}
  Qualifiers = "{ups_qualifiers}"
  Action = FlavorQualSetup
''')
        postamble = w.format('''
Common:
  Action = setup
    setupenv()
    proddir()
    exeActionRequired(FlavorQualSetup)
End:\n''')

        meat = []

        for mystep, deppkg, deppkgstep in w.dependencies():
            o = w.others[deppkg]
            depquals = ''
            if o.ups_qualifiers:
                depquals = ' -q ' + o.ups_qualifiers
            s = w.format('setupRequired( {deppkg} {depver} {depquals} )',
                         deppkg=deppkg, depver='v'+o.version_underscore, depquals=depquals)
            meat.append(s)

        for var, val, oper in w.userenvs():
            #relval = wash_path(val, pdir)
            relval = wash_path(val, idir)
            if relval:
                val = '${UPS_PROD_DIR}/' + relval
            if oper == 'set':
                meat.append('envSet(%s,%s)' % (var, val))
            if oper == 'prepend':
                meat.append('pathPrepend(%s,%s)' % (var, val))
            if oper == 'append':
                meat.append('pathAppend(%s,%s)' % (var, val))
        

        meats = '\n'.join(['    %s' % x for x in meat])

        tf = task.outputs[0]
        tf.write(preamble + meats + postamble)

    tgen.step('upstable',
              rule = upstable,
              update_outputs = True,
              target = table_node)


    def upsversion(task):

        text = w.format('''\
FILE = version
PRODUCT = {ups_product_name}
VERSION = {ups_product_version}
FLAVOR = {ups_flavor}
QUALIFIERS = "{ups_qualifiers}"
  DECLARER = {user}
  DECLARED = {date}
  MODIFIER = {user}
  MODIFIED = {date}
  PROD_DIR = {ups_product_subdir}
  TABLE_DIR = {ups_table_dir}
  TABLE_FILE = {ups_table_file}\n''',
                           user=os.environ.get('USER','worch'), 
                           date=time.asctime(time.gmtime()) + ' GMT')
        tf = task.outputs[0]
        tf.write(text)
        
    tgen.step('upsversion',
              rule = upsversion,
              update_outputs = True,
              target = version_node)

    # this functionality should be largely moved into python-ups-utils
    def upspack(task):
        tf = tarfile.open(task.outputs[0].abspath(), mode='w:bz2')
        # installation dir
        tf.add(idir.abspath(),
               arcname = wash_path(pdir.abspath(), repo), recursive=True)

        # if product dirs do not coincide with install dirs then the
        # version and table files need to be explicitly added.

        # ups version file
        name = wash_path(task.inputs[0].abspath(), repo)
        if name not in tf.getnames():
            tf.add(task.inputs[0].abspath(), arcname=name)

        # ups table file
        name = wash_path(table_node.abspath(), repo)
        if name not in tf.getnames():
            tf.add(table_node.abspath(), arcname=name)

    tgen.step('upspack',
              rule = upspack,
              source = [version_node, table_node, tgen.control_node('install')],
              target = w.format('upspack/{ups_tarball_package}'))


