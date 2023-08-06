"""
mbase module
  This module contains the base model and base package classes from which
  all of the other models and packages inherit from.

"""

import numpy as np
from numpy.lib.recfunctions import stack_arrays
import sys
import os
import subprocess as sp
import webbrowser as wb
import warnings
from modflow.mfparbc import ModflowParBc as mfparbc


# Global variables
iconst = 1 # Multiplier for individual array elements in integer and real arrays read by MODFLOW's U2DREL, U1DREL and U2DINT.
iprn = -1 # Printout flag. If >= 0 then array values read are printed in listing file.


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        # test for exe in current working directory
        if is_exe(program):
            return program
        # test for exe in path statement
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


class BaseModel(object):
    """
    MODFLOW based models base class

    Parameters
    ----------

    modelname : string
        Name of the model.  Model files will be given this name. (default is
        'modflowtest'

    namefile_ext : string
        name file extension (default is 'nam')

    exe_name : string
        name of the modflow executable

    model_ws : string
        Path to the model workspace.  Model files will be created in this
        directory.  Default is None, in which case model_ws is assigned
        to the current working directory.

    """
    def __init__(self, modelname='modflowtest', namefile_ext='nam',
                 exe_name='mf2k.exe', model_ws=None):
        """
        BaseModel init
        """
        self.__name = modelname
        self.namefile_ext = namefile_ext
        self.namefile = self.__name + '.' + self.namefile_ext
        self.packagelist = []
        self.heading = ''
        self.exe_name = exe_name
        self.external_extension = 'ref'
        if model_ws is None: model_ws = os.getcwd()
        if not os.path.exists(model_ws):
            try:
                os.makedirs(model_ws)
            except:
                #print '\n%s not valid, workspace-folder was changed to %s\n' % (model_ws, os.getcwd())
                print '\n{0:s} not valid, workspace-folder was changed to {1:s}\n'.format(model_ws, os.getcwd())
                model_ws = os.getcwd()
        self.model_ws= model_ws
        self.pop_key_list = []
        self.cl_params = ''
        return

    def set_exename(self, exe_name):
        """
        Set the name of the executable.

        Parameters
        ----------
        exe_name : name of the executable

        """
        self.exe_name = exe_name
        return
        
    def add_package(self, p):
        """
        Add a package.

        Parameters
        ----------
        p : Package object

        """
        for i, pp in enumerate(self.packagelist):
            if pp.allowDuplicates:
                continue
            elif (isinstance(p, type(pp))):
                print '****Warning -- two packages of the same type: ',type(p),type(pp)                 
                print 'replacing existing Package...'
                self.packagelist[i] = p
                return        
        if self.verbose:
            print 'adding Package: ', p.name[0]
        self.packagelist.append(p)
    
    def remove_package(self, pname):
        """
        Remove a package from this model

        Parameters
        ----------
        pname : string
            Name of the package, such as 'RIV', 'BAS6', etc.

        """
        for i, pp in enumerate(self.packagelist):
            if pname in pp.name:
                if self.verbose:
                    print 'removing Package: ', pp.name
                self.packagelist.pop(i)
                return
        raise StopIteration , 'Package name '+pname+' not found in Package list'

    def __getattr__(self, item):
        """
        __getattr__ - syntactic sugar

        Parameters
        ----------
        item : str
            3 character package name (case insensitive)

        Returns
        -------
        pp : Package object
            Package object of type :class:`flopy.mbase.Package`

        """
        return self.get_package(item)

    def build_array_name(self, num, prefix):
        """
        Build array name

        Parameters
        ----------
        num : int
            array number
        prefix : string
            array prefix

        """
        return self.external_path + prefix + '_' + str(num) + '.' + self.external_extension
       
    def assign_external(self, num, prefix):
        """
        Assign external file

        Parameters
        ----------
        num : int
            array number
        prefix : string
            array prefix

        """
        fname = self.build_array_name(num, prefix)
        unit = (self.next_ext_unit())
        self.external_fnames.append(fname)
        self.external_units.append(unit)       
        self.external_binflag.append(False)        
        return fname, unit
    
    def add_external(self, fname, unit, binflag=False):
        """
        Assign an external array so that it will be listed as a DATA or
        DATA(BINARY) entry in the name file.  This will allow an outside
        file package to refer to it.

        Parameters
        ----------
        fname : str
            filename of external array
        unit : int
            unit number of external array
        binflag : boolean
            binary or not. (default is False)

        """
        self.external_fnames.append(fname)
        self.external_units.append(unit)        
        self.external_binflag.append(binflag)
        return
    
    def remove_external(self, fname=None, unit=None):
        """
        Remove an external file from the model by specifying either the
        file name or the unit number.

        Parameters
        ----------
        fname : str
            filename of external array
        unit : int
            unit number of external array

        """
        if fname is not None:
            for i, e in enumerate(self.external_fnames):
                if fname in e:
                    self.external_fnames.pop(i)
                    self.external_units.pop(i)
                    self.external_binflag.pop(i)
        elif unit is not None:
            for i, u in enumerate(self.external_units):
                if u == unit:
                    self.external_fnames.pop(i)
                    self.external_units.pop(i)
                    self.external_binflag.pop(i)
        else:
            raise Exception,' either fname or unit must be passed to remove_external()'
        return            

    def get_name_file_entries(self):
        """
        Get a string representation of the name file.

        Parameters
        ----------

        """
        s = ''
        for p in self.packagelist:
            for i in range(len(p.name)):
                s = s + ('{0:12s} {1:3d} {2:s} {3:s}\n'.format(p.name[i],
                                                             p.unit_number[i],
                                                             p.file_name[i],
                                                             p.extra[i]))
        return s
                
    def get_package(self, name):
        """
        Get a package.

        Parameters
        ----------
        name : str
            Name of the package, 'RIV', 'LPF', etc.

        Returns
        -------
        pp : Package object
            Package object of type :class:`flopy.mbase.Package`

        """
        for pp in (self.packagelist):
            if (pp.name[0].upper() == name.upper()):
                return pp
        return None
   
    def get_package_list(self):
        """
        Get a list of all the package names.

        Parameters
        ----------

        Returns
        -------
        val : list of strings
            Can be used to see what packages are in the model, and can then
            be used with get_package to pull out individual packages.

        """
        val = []
        for pp in (self.packagelist):
            val.append(pp.name[0].upper())
        return val
    
    def change_model_ws(self, new_pth=None):
        """
        Change the model work space.

        Parameters
        ----------
        new_pth : str
            Location of new model workspace.  If this path does not exist,
            it will be created. (default is None, which will be assigned to
            the present working directory).

        Returns
        -------
        val : list of strings
            Can be used to see what packages are in the model, and can then
            be used with get_package to pull out individual packages.

        """
        if new_pth is None:
            new_pth = os.getcwd()
        if not os.path.exists(new_pth):
            try:
                sys.stdout.write('\ncreating model workspace...\n   {}\n'.format(new_pth))
                os.makedirs(new_pth)
            except:
                #print '\n%s not valid, workspace-folder was changed to %s\n' % (new_pth, os.getcwd())
                print '\n{0:s} not valid, workspace-folder was changed to {1:s}\n'.format(new_pth, os.getcwd())
                new_pth = os.getcwd()
        #--reset the model workspace
        self.model_ws = new_pth
        sys.stdout.write('\nchanging model workspace...\n   {}\n'.format(new_pth))
        #--reset the paths for each package
        for pp in (self.packagelist):
            pp.fn_path = os.path.join(self.model_ws, pp.file_name[0])

        return None
    
    def run_model(self, silent=False, pause=False, report=False):
        """
        This method will run the model using subprocess.Popen.

        Parameters
        ----------
        silent : boolean
            Echo run information to screen (default is True).
        pause : boolean, optional
            Pause upon completion (the default is False).
        report : string, optional
            Name of file to store stdout. (default is None).

        Returns
        -------
        (success, buff)
        success : boolean
        buff : list of lines of stdout

        """
        success = False
        buff = []

        # Check to make sure that program and namefile exist
        exe = which(self.exe_name)
        if exe is None:
            s = 'The program {} does not exist or is not executable.'.format(self.exe_name)
            raise Exception(s)
        else:
            if not silent:
                s = 'FloPy is using the following executable to run the model: {}'.format(exe)
                print (s)

        if not os.path.isfile(os.path.join(self.model_ws, self.namefile)):
            s = 'The namefile for this model does not exists: {}'.format(self.namefile)
            raise Exception(s)

        proc = sp.Popen([self.exe_name, self.namefile],
                        stdout=sp.PIPE, cwd=self.model_ws)
        while True:
          line = proc.stdout.readline()
          if line != '':
            if 'normal termination of simulation' in line.lower():
                success = True
            #c = line.split('\r')
            c = line.rstrip('\r\n')
            if not silent:
                print c
            if report == True:
                buff.append(c)
          else:
            break
        if pause == True:
            raw_input('Press Enter to continue...')
        return ([success, buff])
        
    def write_input(self, SelPackList=False):
        """
        Write the input.

        Parameters
        ----------
        SelPackList : False or list of packages

        """
        #org_dir = os.getcwd()
        #os.chdir(self.model_ws)
        if self.verbose:
            print '\nWriting packages:'
        if SelPackList == False:
            for p in self.packagelist:            
                if self.verbose:
                    print '   Package: ', p.name[0]
                p.write_file()
        else:
            for pon in SelPackList:
                for i, p in enumerate(self.packagelist):
                    if pon in p.name:
                        if self.verbose:
                            print '   Package: ', p.name[0]
                        p.write_file()
                        break
        if self.verbose:
            print ' '
        #--write name file
        self.write_name_file()
        #os.chdir(org_dir)
        return
    
    def write_name_file(self):
        """
        Every Package needs its own writenamefile function

        """
        raise Exception, 'IMPLEMENTATION ERROR: writenamefile must be overloaded'

    def get_name(self):
        """
        Get model name

        Returns
        -------
        name : str
            name of model

        """
        return self.__name

    def set_name(self, value):
        """
        Set model name

        Parameters
        ----------
        value : str
            Name to assign to model.

        """
        self.__name = value
        self.namefile = self.__name + '.' + self.namefile_ext
        for p in self.packagelist:
            for i in range(len(p.extension)):
                p.file_name[i] = self.__name + '.' + p.extension[i]
    name = property(get_name, set_name)

    def add_pop_key_list(self, key):
        """
        Add a external file unit number to a list that will be used to remove
        model output (typically binary) files from ext_unit_dict.

        Parameters
        ----------
        key : int
            file unit number

        Returns
        -------

        Examples
        --------

        """
        if key not in self.pop_key_list:
            self.pop_key_list.append(key)


class Package(object):
    """
    Base package class from which most other packages are derived.

    """
    def __init__(self, parent, extension='glo', name='GLOBAL', unit_number=1, extra='', 
                 allowDuplicates=False):
        """
        Package init

        """
        self.parent = parent # To be able to access the parent modflow object's attributes
        if (not isinstance(extension, list)):
            extension = [extension]
        self.extension = []
        self.file_name = []
        for e in extension:
            self.extension = self.extension + [e]
            self.file_name = self.file_name + [self.parent.name + '.' + e]
            self.fn_path = os.path.join(self.parent.model_ws,self.file_name[0])
        if (not isinstance(name, list)):
            name = [name]
        self.name = name
        if (not isinstance(unit_number, list)):
            unit_number = [unit_number]
        self.unit_number = unit_number
        if (not isinstance(extra, list)):
            self.extra = len(self.unit_number) * [extra]
        else:
            self.extra = extra
        self.url = 'index.html'
        self.allowDuplicates = allowDuplicates

        self.acceptable_dtypes = [int,np.float32,str]
        return

    def __repr__(self):
        s = self.__doc__
        exclude_attributes = ['extension', 'heading', 'name', 'parent', 'url']
        for attr, value in sorted(self.__dict__.iteritems()):
            if not (attr in exclude_attributes):
                if (isinstance(value, list)):
                    if (len(value) == 1):
                        #s = s + ' %s = %s (list)\n' % (attr, str(value[0]))
                        s = s + ' {0:s} = {1:s}\n'.format(attr,str(value[0]))
                    else:
                        #s = s + ' %s (list, items = %d)\n' % (attr, len(value))
                        s = s + ' {0:s} (list, items = {1:d}\n'.format(attr,len(value))
                elif (isinstance(value, np.ndarray)):
                    #s = s + ' %s (array, shape = %s)\n' % (attr, value.shape.__str__()[1:-1] )
                    s = s + ' {0:s} (array, shape = {1:s}\n'.fomrat(attr,value.shape__str__()[1:-1])
                else:
                    #s = s + ' %s = %s (%s)\n' % (attr, str(value), str(type(value))[7:-2])
                    s = s + ' {0:s} = {1:s} ({2:s}\n'.format(attr,str(value),str(type(value))[7:-2])
        return s

    def __getitem__(self, item):
        if not isinstance(item,list) and not isinstance(item,tuple):
            assert item in self.stress_period_data.data.keys(),"package.__getitem__() kper "+str(item)+" not in data.keys()"
            return self.stress_period_data[item]

        if item[1] not in self.dtype.names:
            raise Exception ("package.__getitem(): item \'"+item+"\' not in dtype names "+str(self.dtype.names))
        assert item[0] in self.stress_period_data.data.keys(),"package.__getitem__() kper "+str(item[0])+" not in data.keys()"
        if self.stress_period_data.vtype[item[0]] == np.recarray:
            return self.stress_period_data[item[0]][item[1]]

    def __setitem__(self, key, value):
        raise NotImplementedError("package.__setitem__() not implemented")

    @staticmethod
    def add_to_dtype(dtype,field_names,field_types):
        if not isinstance(field_names,list):
            field_names = [field_names]
        if not isinstance(field_types,list):
            field_types = [field_types] * len(field_names)
        newdtypes = [dtype]
        for field_name,field_type in zip(field_names,field_types):
            tempdtype = np.dtype([(field_name,field_type)])
            newdtypes.append(tempdtype)
        newdtype = sum((dtype.descr for dtype in newdtypes), [])
        newdtype = np.dtype(newdtype)
        return newdtype

    def webdoc(self):
        if self.parent.version == 'mf2k':
            wb.open('http://water.usgs.gov/nrp/gwsoftware/modflow2000/Guide/' + self.url)
        elif self.parent.version == 'mf2005':
            wb.open('http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/' + self.url)
        elif self.parent.version == 'ModflowNwt':
            wb.open('http://water.usgs.gov/ogw/modflow-nwt/MODFLOW-NWT-Guide/' + self.url)

    def write_file(self):
        """
        Every Package needs its own write_file function

        """
        print 'IMPLEMENTATION ERROR: write_file must be overloaded'
        return

    @staticmethod
    def load(model, pack_type, f, nper=None, pop_key_list=None):
        """
        The load method has not been implemented for this package.

        """

        bc_pack_types = []

        if type(f) is not file:
            filename = f
            f = open(filename, 'r')
        #dataset 0 -- header
        while True:
            line = f.readline()
            if line[0] != '#':
                break
        #--check for parameters
        nppak = 0
        if "parameter" in line.lower():
            t = line.strip().split()
            #assert int(t[1]) == 0,"Parameters are not supported"
            nppak = np.int(t[1])
            mxl = 0
            if nppak > 0:
                mxl = np.int(t[2])
                if model.verbose:
                    print '   Parameters detected. Number of parameters = ', nppak
            line = f.readline()
        #dataset 2a
        t = line.strip().split()
        ipakcb = 0
        try:
            if int(t[1]) != 0:
                ipakcb = 53
                pop_key_list = model.pop_key_list(int(t[1]), pop_key_list)
        except:
            pass
        options = []
        aux_names = []
        if len(t) > 2:
            it = 2
            while it < len(t):
                toption = t[it]
                if toption.lower() is 'noprint':
                    options.append(toption)
                elif 'aux' in toption.lower():
                    options.append(' '.join(t[it:it+2]))
                    aux_names.append(t[it+1].lower())
                    it += 1
                it += 1
        
        #--set partype
        #  and read phiramp for modflow-nwt well package
        partype = ['cond']
        if 'flopy.modflow.mfwel.modflowwel'.lower() in str(pack_type).lower():
            partype = ['flux']
            specify = False
            ipos = f.tell()
            line = f.readline()
            #--test for specify keyword if a NWT well file - This is a temporary hack
            if 'specify' in line.lower():
                specify = True
                line = f.readline() #ditch line -- possibly save for NWT output
                t = line.strip().split()
                phiramp = np.float32(t[1])
                try:
                    phiramp_unit = np.int32(t[2])
                except:
                    phiramp_unit = 2
                options.append('specify {} {} '.format(phiramp, phiramp_unit))
            else:
                f.seek(ipos)
        elif 'flopy.modflow.mfchd.modflowchd'.lower() in str(pack_type).lower():
            partype = ['shead', 'ehead']

        #--read parameter data
        if nppak > 0:
            dt = pack_type.get_empty(1, aux_names=aux_names).dtype
            pak_parms = mfparbc.load(f, nppak, dt, model.verbose)
            #pak_parms = mfparbc.load(f, nppak, len(dt.names))

        if nper is None:
            nrow, ncol, nlay, nper = model.get_nrow_ncol_nlay_nper()
        
        
        #read data for every stress period
        bnd_output = None
        stress_period_data = {}
        for iper in xrange(nper):
            if model.verbose:
                print "   loading "+str(pack_type)+" for kper {0:5d}".format(iper+1)
            line = f.readline()
            if line == '':
                break
            t = line.strip().split()
            itmp = int(t[0])
            itmpp = 0
            try:
                itmpp = int(t[1])
            except:
                pass
            
            if itmp == 0:
                bnd_output = None
                current = pack_type.get_empty(itmp, aux_names=aux_names)
            elif itmp > 0:
                current = pack_type.get_empty(itmp, aux_names=aux_names)
                for ibnd in xrange(itmp):
                    line = f.readline()
                    if "open/close" in line.lower():
                        raise NotImplementedError("load() method does not support \'open/close\'")
                    try:
                        t = line.strip().split()
                        current[ibnd] = tuple(t[:len(current.dtype.names)])
                    except:
                        t = []
                        for ivar in xrange(len(current.dtype.names)):
                            istart = ivar * 10
                            istop = istart + 10
                            t.append(line[istart:istop])
                        current[ibnd] = tuple(t[:len(current.dtype.names)])

                #--convert indices to zero-based
                current['k'] -= 1
                current['i'] -= 1
                current['j'] -= 1
                
                bnd_output = np.recarray.copy(current)
            else:
                bnd_output = np.recarray.copy(current)

            for iparm in xrange(itmpp):
                line = f.readline()
                t = line.strip().split()
                pname = t[0].lower()
                iname = 'static'
                try:
                    tn = t[1]
                    c = tn.lower()
                    instance_dict = pak_parms.bc_parms[pname][1]
                    if c in instance_dict:
                        iname = c
                    else:
                        iname = 'static'
                except:
                    pass
                #print pname, iname
                par_dict, current_dict = pak_parms.get(pname)
                data_dict = current_dict[iname]
                #print par_dict
                #print data_dict
                
                par_current = pack_type.get_empty(par_dict['nlst'],aux_names=aux_names)
                
                #--
                #parval = np.float(par_dict['parval'])
                if model.mfpar.pval is None:
                    parval = np.float(par_dict['parval'])
                else:
                    try:
                        parval = np.float(model.mfpar.pval.pval_dict[pname])
                    except:
                        parval = np.float(par_dict['parval'])

                #--fill current parameter data (par_current)
                for ibnd, t in enumerate(data_dict):
                    par_current[ibnd] = tuple(t[:len(par_current.dtype.names)])
                    
                par_current['k'] -= 1
                par_current['i'] -= 1
                par_current['j'] -= 1

                for ptype in partype:
                    par_current[ptype] *= parval
                 
                if bnd_output is None:
                    bnd_output = np.recarray.copy(par_current)
                else:
                    bnd_output = stack_arrays((bnd_output, par_current), 
                                              asrecarray=True, usemask=False)
                     
            if bnd_output is None:
                stress_period_data[iper] = itmp
                #print 'crap'
            else: 
                stress_period_data[iper] = bnd_output
                #print bnd_output.shape
                #print bnd_output   
                
        pak = pack_type(model, ipakcb=ipakcb,
                        stress_period_data=stress_period_data,\
                        dtype=pack_type.get_empty(0,aux_names=aux_names).dtype,\
                        options=options)
        return pak
