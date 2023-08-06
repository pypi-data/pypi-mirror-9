import os
import re
import shelve
import plot as plt
from collections import OrderedDict

from pandas import Series
from pandas import DataFrame
from pandas import concat

from MultiFrame import MultiFrame
import io


Series.__repr__ = (lambda x: ("Hash: {}\nTimes: {}\nLoc: {}\nValues: {}".format(
                    io.hash_series(x),
                    list(set(x.keys().get_level_values('Time'))), # avoid back and forth conversion
                    list(set(x.keys().get_level_values('Loc'))),
                    x.values))) #TODO monkey patch to use hashes
Database = False

if Database:
    case_data_base = shelve.open(os.path.expanduser('~') + "/.owls/db")
else:
    case_data_base = dict() 

def items_from_dict(dict, func, **kwargs):
    return Cases([func(folder=folder,name=name, symb=symb, **kwargs)
               for name, (folder,symb) in dict.iteritems()])

def read_sets(folder, name="None", search="(postProcessing/)*sets/" + io.FPNUMBER, **kwargs):
    return FoamFrame(folder=folder, search_files=False,
            search_pattern=search, name=name,
            show_func="plot", preHooks=None, **kwargs)

def read_lag(folder, files, skiplines=1,
        name="None", cloud="[A-Za-z]*Cloud1",
        preHooks=None, decomposed=False, **kwargs
    ):
    search = io.FPNUMBER + "/lagrangian/" + cloud,
    search = (search if not decomposed else "processor[0-9]?/" + search)
    return FoamFrame(folder=folder, search_files=files,
                search_pattern=search, name=name, skiplines=skiplines,
                show_func="scatter", **kwargs)

def read_eul(folder, files, skiplines=1, name="None", decomposed=False,
            preHooks=None, **kwargs):
    search = io.FPNUMBER
    search = (search if not decomposed else "processor[0-9]?/" + search)
    return FoamFrame(folder=folder, search_files=files,
            search_pattern=search, name=name,
            skiplines=skiplines, show_func="scatter", preHooks=preHooks,
             **kwargs)

def read_exp(folder, name="None", search="", **kwargs):
    return FoamFrame(folder=folder, search_files=False,
             search_pattern=search, name=name, show_func="scatter", **kwargs)


def read_log(folder, keys, log_name='*log*', plot_properties=False):
    origins,df = io.import_logs(folder,keys)
    ff = FoamFrame(df)
    ff.properties=Props(
            origins=origins,
            name='LogFiles',
            plot_properties=plot_properties,
            folder=folder,
            times=[0],
            symb="-",
            show_func="plot",
            )
    return ff

class PlotProperties():

    def __init__(self):
        from collections import defaultdict
        self.properties = defaultdict(dict)

    def insert(self, field, properties):
        self.properties[field].update(properties)
        return self

    def select(self, field, prop, default=None):
        field = self.properties[field]
        if not field:
            return
        else:
            return field.get(prop, default)

class Props():

    def __init__(self, origins, name,
            plot_properties, folder, times, symb,show_func,):
        self.origins=origins
        self.name=name
        self.plot_properties=plot_properties
        self.folder=folder
        self.times=times
        self.latest_time = max(times)
        self.symb=symb
        self.show_func=show_func


class FoamFrame(DataFrame):
    """ Data reprensentation of OpenFOAM field (eulerian and lagrangian)
    and set files. Instantiated through read methods, e.g:
    read_sets, read_lag, read_eul, read_exp


    Examples:
    ----------

    case = read_sets(folder="home/user/case",plot_properties={})
    case.data # access data frame

    Parameters:
    ----------
    folder: data location containing a time or sets folder
    files: search only for files with given name, None for all files
    plot_properties: dictionary for consistent plotting of ranges and ax labels
    skiplines: read only every n-th entry
    cloud: name of lagrangian cloud
    name: case name for plot legends

    Note:
    ----------

    If data is accessed through [] only latest item is returned. For full times
    access iteratetimes() can be used.

    Categories:

        { "rad_pos": lambda field -> position
          "centreLine": [] lambda field -> i of []

        }

        example:
            lambda field: re.search('[0-9]*\.[0-9]*').group()[0]

    TODO:
        use case as cases ojects with a 3-level index
             case['u']
             acces time of all cases -> df.iloc[df.index.isin([1],level=1)]
        refactor plot into case objects itself,
            ?case.show('t','u', time_series = False)
        refactor origins
        make iteratetimes() access a delta
    """
    def __init__(self, *args, **kwargs):

      skip = kwargs.get('skiplines', 1)
      times = kwargs.get('skiptimes', 1)
      name = kwargs.get('name', 'None')
      symb = kwargs.get('symb', 'o')
      files = kwargs.get('search_files', None)
      properties = kwargs.get('properties', None)
      lines = kwargs.get('maxlines', 0)
      search = kwargs.get('search_pattern', io.FPNUMBER)
      folder = kwargs.get('folder', None)
      plot_properties = kwargs.get('plot_properties', PlotProperties())
      show_func = kwargs.get('show_func', None)
      validate = kwargs.get('validate', True)
      preHooks = kwargs.get('preHooks', None)

      keys = [
          'skiplines',
          'skiptimes',
          'preHooks',
          'name',
          'symb',
          'search_files',
          'properties',
          'maxlines',
          'search_pattern',
          'folder',
          'plot_properties',
          'show_func']

      for k in keys:
        try:
            kwargs.pop(k)
        except:
            pass

      #TODO explain what happens here
      if folder == None:
           #super(FoamFrame, self).__init__(*args, **kwargs)
           DataFrame.__init__(self, *args, **kwargs)
      else:
           if preHooks:
                for hook in preHooks:
                    hook.execute()
           if case_data_base.has_key(folder) and Database:
                print "re-importing",
           else:
                print "importing",
           print name + ": ",
           origins, data = io.import_foam_folder(
                       path=folder,
                       search=search,
                       files=files,
                       skiplines=skip,
                       maxlines=lines,
                       skiptimes=times,
                  )
           DataFrame.__init__(self, data)
           self.properties = Props(
                origins,
                name,
                plot_properties,
                folder,
                # FIXME fix it for read logs
                data.index.levels[0],
                symb,
                show_func)
           if validate and Database:
                self.validate_origins(folder, origins)
           # register to database
           if Database:
                case_data_base.sync()

    def validate_origins(self, folder, origins):
        origins.update_hashes()
        if case_data_base.has_key(folder):
            if (case_data_base[folder]["hash"] == origins.dct["hash"]):
                print " [consistent]"
            else:
                entries_new = len(origins.dct.keys())
                entries_old = len(case_data_base[folder].keys())
                if entries_new > entries_old:
                    print "[new timestep] "
                    # print origins.dct.keys()
                    case_data_base[folder] = origins.dct
                elif entries_new < entries_old:
                    # print folder
                    # print origins.dct.keys()
                    # print case_data_base[folder].keys()
                    print "[missing timestep]"
                    case_data_base[folder] = origins.dct
                elif entries_new == entries_old:
                    print "[corrupted]",
                    for time, loc, field, item in origins.hashes():
                        time_name, time_hash   = time
                        loc_name, loc_hash     = loc
                        field_name, field_hash = field
                        filename, item_hash    = item
                        try:
                            orig_hash = case_data_base[folder][time_name][loc_name][field_name][1]
                        except:
                            orig_hash = item_hash
                        if (item_hash != orig_hash):
                            print ""
                            print "corrupted fields:"
                            print "\t" + field_name + " in " +  filename
                    case_data_base[folder] = origins.dct
        else:
            case_data_base[folder] = origins.dct

    def add(self, data, label):
        """
        Add a given Series

        Usage:
        ------ing-
        case.add(sqrt(uu),'u_rms')
        """
        self.latest[label] = data
        return self

    def source(self, col):
        """ find corresponding file for column """
        # return get time loc  and return dict for every column
        # latest.source['u']
        return

    def __str__(self):
        ret =  "FoamFrame: \n" + super(FoamFrame,self).__str__()
        return ret

    @property
    def _constructor(self):
        # override DataFrames constructor
        # to enable method chaining
        return FoamFrame

    @property
    def times(self):
        """ return times for case """
        return set([_[0] for _ in self.index.values])

    @property
    def locations(self):
        """ return times for case """
        return set([_[1] for _ in self.index.values])


    @property
    def latest(self):
        """ return latest time for case """
        ret = self.loc[[self.properties.latest_time]]
        ret.properties = self.properties
        return ret

    # def _iter_names(self)
    #     pass
    #
    # def get_hashes(self):
    #     """ returns hashes of current selection based
    #         on the data read from disk """
    #     pass

    def at(self, idx_name, idx_val):
        """ select from foamframe based on index name and value"""
        ret = self[self.index.get_level_values(idx_name) == idx_val]
        ret.properties = self.properties
        return ret

    def id(self, loc):
        """ Return FoamFrame based on location """
        return self.at(idx_name='Id', idx_val=loc)

    def location(self, loc):#
        """ Return FoamFrame based on location """
        return self.at(idx_name='Loc', idx_val=loc)

    def loc_names(self, key):
        """ search for all index names matching keyword"""
        return [_ for _ in  self.index.get_level_values("Loc") if key in _]

    def field_names(self, key):
        """ search for all field names matching keyword"""
        return [_ for _ in  self.columns if key in _]

    def rename(self, search, replace):
        """ rename field names based on regex """
        import re
        self.columns = [re.sub(search, replace, name) for name in self.columns]


    def _is_idx(self, item):
        """ test if item is column or idx """
        return item in self.index.names

    def __getitem__(self, item):
        """ call pandas DataFrame __getitem__ if item is not
            an index
        """
        if self._is_idx(item):
            level = self.index.names.index(item)
            return zip(*self.index.values)[level]
        else:
           return super(FoamFrame, self).__getitem__(item)

    def draw(self, x, y, z, title, func, **kwargs):
        import bokeh.plotting as bk
        #TODO: change colors if y is of list type
        y = (y if type(y) == list else [y]) # wrap y to a list so that we can iterate

        kwargs.update({ "outline_line_color":"black", #FIXME refactor
                        "plot_width":300,
                        "plot_height":300,
                      })
        bk.hold(True)
        for yi in y:
            x_data, y_data = self[x], self[yi]
            func(x=x_data,
                 y=y_data,
                 title=title,
                 **kwargs)
        bk.hold(False)
        ret = bk.curplot()

        def _label(axis, field):
           label = kwargs.get(axis + '_label', False)
           if label:
               self.properties.plot_properties.insert(field, {axis + '_label':label})
           else:
               label = self.properties.plot_properties.select(field, axis + '_label', "None")
           return label

        def _range(axis, field):
           from bokeh.objects import Range1d
           p_range_args = kwargs.get(axis + '_range', False)
           if p_range_args:
               self.properties.plot_properties.insert(field, {axis + '_range': p_range})
           else:
               p_range = self.properties.plot_properties.select(field, axis + '_range')
           if not p_range:
                return False
           else:
                return Range1d(start=p_range[0], end=p_range[1])


        bk.xaxis().axis_label = _label('x', x)
        if _range('x', x):
            ret.x_range = _range('x', x)
        bk.yaxis().axis_label = _label('y', y[0]) #TODO can this make sense for multiplots?
        if _range('y', y[0]):
            ret.y_range = _range('y', y[0])
        return ret

    def scatter(self, y, x='Pos', z=False, title="", **kwargs):
        import bokeh.plotting as bk
        return self.draw(x, y, z, title, func=bk.scatter, **kwargs)

    def plot(self, y, x='Pos', z=False, title="", **kwargs):
        import bokeh.plotting as bk
        return self.draw(x, y, z, title, func=bk.line, **kwargs)


    def show(self, y, x=None, **kwargs):
        if x:
            return getattr(self,self.properties.show_func)(y=y, x=x, **kwargs)
        else:
            return getattr(self,self.properties.show_func)(y=y, **kwargs)


    def filter(self, name, index=None, field=None):
        """ filter on index or field values by given functioni

            Examples:

                .filter(name='T', field=lambda x: 1000<x<2000)
                .filter(name='Loc', index=lambda x: 0.2<field_to_float(x)<0.8)
        """
        if index:
            ret = self[map(index, self.index.get_level_values(name))]
            ret.properties = self.properties
            return ret
        elif field:
            ret = self[map(field,self[name])]
            ret.properties = self.properties
            return ret
        else:
            return self

    def by_index(self, field, func=None):
        func = (func if func else lambda x: x)
        return self.by(field, index=func)


    def by_field(self, field, func=None):
        func = (func if func else lambda x: x)
        return self.by(field, field=func)

    def by(self, name, index=None, field=None):
        """ facet by given function

            Examples:

            .by(index=lambda x: x)
            .by(field=lambda x: ('T_high' if x['T'] > 1000 else 'T_low'))
        """
        if index:
            ret = OrderedDict(
                   [(index(val),self[self.index.get_level_values(name) == val])
                        for val in self.index.get_level_values(name)]
                  )
            for _ in ret.itervalues():
                _.properties = self.properties
            return MultiFrame(ret)
        else:
            self['cat'] = map(field, self[name])
            cats = self.groupby('cat').groups.keys()
            ret =  OrderedDict(
                    [(cat,self[self['cat'] == cat]) for cat in cats]
                )
            for _ in ret.itervalues():
                _.properties = self.properties
            return MultiFrame(ret)

    ############################################################################
    @property
    def vars(self):
        # if self.data.empty:
        #     return
        """ delete this methode and replace by columns ??"""
        print "This Method is obsolete and will be replaced by .columns"
        return self.columns

    # def __getitem__(self, field):
    #     try:
    #         print field
    #         return self.loc[self.latest_time][field]
    #     except Exception as e:
    #         print "%s Warning: requested field %s not in data base" %(self.name, field)
    #         print e
    #         return Series()

  #   def __str__(self):
  #       return """Foam case object
  # Data Fields: {}
  # Total number of items {}
  # Data root: {}""".format(
  #   str([_ for _ in self.vars]), "unknown", self.folder)

    # def reread(self):
    #     """ re-read foam data """
    #     self.origins, self.data = self._read_data()

