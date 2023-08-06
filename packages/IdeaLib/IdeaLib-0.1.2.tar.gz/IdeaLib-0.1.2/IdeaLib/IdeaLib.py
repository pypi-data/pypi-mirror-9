import pandas as pd
import numpy as np
import itertools
import datetime
import copy

class Idea():
    def __init__(self, plan={}, iw=1, ow=1):
        self.time_unit = datetime.timedelta(days=1)
        self.money_unit = 'LTL'
        self.start_time = datetime.datetime.today()
        self.iweights = iw # input weights
        self.oweights = ow # output weights
        if type(plan) in [str,unicode]:
            self.from_idl(plan)
        else:
            self.plan = plan
    def from_idl(self, text):
        ''' Converts a multiline string to self.plan list of tuples of dicts.
            vline: the part of line after @ mark sign
        '''
        result = []
        for i,line in enumerate(text.rstrip().lstrip().split('\n')):
            if '@' in line:
                # for processing value definitions
                line, vline = line.strip().split('@')
                line = line.strip(); vline = vline.strip()
            first_whitespace = line.find(' ')
            #line_to_dict =  lambda x: dict([attribute.strip().split(' ') for attribute in x.split(',')])
            line_to_dict =  lambda x: dict([[' '.join(attribute.strip().split(' ')[:-1]), attribute.strip().split(' ')[-1]] for attribute in x.split(',')])
            split_dict_values = lambda d: dict([(v, d[v].split('\\')) for k,v in enumerate(d)])
            if i % 2 == 0:
                domain = line[first_whitespace:].strip()
                if ' ' not in domain: # just so that line_to_dict would work.
                    domain += ' 1'   
            elif i % 2 == 1:
                codomain = line[first_whitespace:].strip()
                if ' ' not in codomain: # just so that line_to_dict would work.
                    codomain += ' 1'     
                result.append((split_dict_values(line_to_dict(domain)),split_dict_values(line_to_dict(codomain))))
        self.plan = result
        # self.iweights, self.oweights -- define here later from the text.
    def __str__(self):
        return str(self.plan)
    def __repr__(self):
        self.view = ''
        for i, p in enumerate(self.plan):
            if i == 0: self.view += '' + str(p[0]) + '\n:  ' + str(p[1]) +'\n';
            if i > 0: self.view += '' + str(p[0]) + '\n-> ' + str(p[1]) +'\n';
        return self.view
    def _plan_values_to_lists(self):
        ''' Converts Plan Dictionary Values to Lists '''
        for i, x in enumerate(self.plan):
            for j, y in enumerate(self.plan[i]):
                for k, z in enumerate(self.plan[i][j]):
                    self.plan[i][j][z] = [self.plan[i][j][z]] if type(self.plan[i][j][z]) != list else self.plan[i][j][z]
    def scenario_mean_values(self):
        ''' Takes the means for value lists, to be used for mean scenario. '''
        p = copy.deepcopy(self.plan)
        for i,x in enumerate(p):
            for j, y in enumerate(p[i]):
                for k, z in enumerate(p[i][j]):
                    p[i][j][z] = sum([float(val) for val in p[i][j][z]])/len(p[i][j][z]) \
                    if type(self.plan[i][j][z][0]) in [str, int, float] \
                    else p[i][j][z][len(p[i][j][z])/2]
        self.p = p
        self.scenario = p
    def scenario_max_in_min_out(self):
        ''' This takes max values for the domain, and min values for codomain.'''
        p = copy.deepcopy(self.plan)
        for i,x in enumerate(p):
            for j, y in enumerate(p[i]):
                for k, z in enumerate(p[i][j]):
                    if j == 0: # max in.  # it seems max operator works .. for strings too
                        p[i][j][z] = max([float(val) for val in p[i][j][z]]) \
                        if type(self.plan[i][j][z][0]) in [str, int, float] \
                        else float(p[i][j][z][len(p[i][j][z])/2])
                    if j == 1: # min out
                        p[i][j][z] = min([float(val) for val in p[i][j][z]]) \
                        if type(self.plan[i][j][z][0]) in [str, int, float] \
                        else float(p[i][j][z][len(p[i][j][z])/2])
        self.p = p
        self.scenario = p
    def scenario_min_in_max_out(self):
        ''' This takes max values for the domain, and min values for codomain.'''
        p = copy.deepcopy(self.plan)
        for i,x in enumerate(p):
            for j, y in enumerate(p[i]):
                for k, z in enumerate(p[i][j]):
                    if j == 0: # min in
                        p[i][j][z] = min([float(val) for val in p[i][j][z]]) \
                        if type(self.plan[i][j][z][0]) in [str, int, float] \
                        else float(p[i][j][z][len(p[i][j][z])/2])
                    if j == 1: # max out
                        p[i][j][z] = max([float(val) for val in p[i][j][z]]) \
                        if type(self.plan[i][j][z][0]) in [str, int, float] \
                        else float(p[i][j][z][len(p[i][j][z])/2])
        self.p = p
        self.scenario = p
    def scenario_n(self,n=0):
        ''' This takes mean values for the domain, and nth values for codomain.'''
        p = copy.deepcopy(self.plan)
        for i,x in enumerate(p):
            for j, y in enumerate(p[i]):
                for k, z in enumerate(p[i][j]):
                    if j == 0: # domain
                        p[i][j][z] = sum(p[i][j][z])/len(p[i][j][z]) \
                        if type(self.plan[i][j][z][0]) in [int, float] \
                        else p[i][j][z][len(p[i][j][z])/2]
                    if j == 1: # codomain
                        p[i][j][z] = p[i][j][z][n] \
                        if len(self.plan[i][j][z])+1 >= n \
                        else p[i][j][z][min(n,len(p[i][j][z]-1))]
        self.p = p
        self.scenario = p        
    def _plan_add_dummy_index_keys(self):
        ''' Unifies the domain index. '''
        types, index, values = zip(*[[t[0].keys(),tuple(t[0].values()), t[1]] for l,t in enumerate(self.plan)])
        types = set(itertools.chain(*types))
        for i, x in enumerate(self.plan):
            absent_keys = types - set(self.plan[i][0].keys())
            self.plan[i] = (dict(self.plan[i][0], **dict(zip(absent_keys, [[0]]*(len(absent_keys))))), self.plan[i][1])
    def to_df(self, scenario='normal', dates=False, value=False, iweights=False, oweights=False, resample=False, fill=False, silent=False, convert='numeric', cumsum=False):
        ''' Converts a scenario to DataFrame. '''
        self.u = self._plan_values_to_lists()
        self.v = self._plan_add_dummy_index_keys()
        if scenario == 'normal':
            self.scenario_mean_values()
        if scenario == 'best':
            self.scenario_min_in_max_out()
        if scenario == 'worst':
            self.scenario_max_in_min_out()
        if type(scenario) == int:
            self.scenario_n(scenario)
        # essential piece constructing dataframe: the index:  tuple(t[0].values()), the values: t[1]
        self.d1 = pd.DataFrame.from_records([r[0] for r in self.p])
        self.d2 = pd.DataFrame.from_records([r[1] for r in self.p])
        self.df = pd.concat([self.d1,self.d2],axis=1).set_index(list(self.d1.columns))
        # Great :)
        if convert == 'numeric':
            self.df = self.df.convert_objects(convert_numeric=True)
            self.d1 = self.d1.convert_objects(convert_numeric=True)
            self.d2 = self.d2.convert_objects(convert_numeric=True)
        # Will need to make so that value = ovalue - ivalue
        # Basically:                value = self.d2*ovalue - self.d1*ivalue 
        # input value
        if iweights:
            self.iweights = iweights
        if type(self.iweights)==int:
            self.iweights = len(self.d1.columns)*[self.iweights]
        if type(self.iweights)==bool:
            self.iweights = len(self.d1.columns)*[1]
        if type(self.iweights)==dict:
            self.iweights = [self.iweights[key] if key in self.iweights.keys() else 0 for key in self.df.index.names]
        if type(self.iweights)==list:
            if len(self.iweights) < len(self.d1.columns):
                self.iweights += [0]*(len(self.d1.columns)-len(self.iweights))
            else:
                self.iweights = self.iweights[0:len(self.d1.columns)]
        if type(self.iweights)==dict:
            pass
        self.d1  = pd.DataFrame(self.d1.values, index=self.df.index, columns=self.d1.columns)
        self.d1['ivalue'] = (self.d1*self.iweights).sum(axis=1)
        # output value
        if oweights:
            self.oweights = oweights
        if type(self.oweights)==int:
            self.oweights = len(self.d2.columns)*[self.oweights]
        if type(self.oweights)==bool:
            self.oweights = len(self.d2.columns)*[1]
        if type(self.oweights)==dict:
            self.oweights = [self.oweights[key] if key in self.oweights.keys() else 0 for key in self.df.columns]
        if type(self.oweights)==list:
            if len(self.oweights) < len(self.df.columns):
                self.oweights += [0]*(len(self.df.columns)-len(self.oweights))
            else:
                self.oweights = self.oweights[0:len(self.df.columns)]
        if type(self.oweights)==dict:
            pass
        self.d2  = pd.DataFrame(self.d2.values, index=self.df.index, columns=self.d2.columns)
        self.d2['ovalue'] = (self.d2*self.oweights).sum(axis=1)
        # value
        if self.iweights and self.oweights:
            self.df['ivalue'] = self.d1['ivalue']
            self.df['ovalue'] = self.d2['ovalue']
            self.df['value'] = self.d2['ovalue']-self.d1['ivalue']
        elif self.iweights:
            self.df['ivalue'] = self.d1['ivalue']
            self.df['ovalue'] = np.nan
            self.df['value'] = self.d1['ivalue']
        elif self.oweights:
            self.df['ivalue'] = np.nan
            self.df['ovalue'] = self.d2['ovalue']
            self.df['value'] = self.d2['ovalue']
        if dates:
            df = self.df.reset_index()
            if 'time' not in df.columns:
                df['time'] = 0
            df['time'] = df['time'].convert_objects(convert_numeric=True).apply(lambda x: datetime.timedelta(seconds=self.time_unit.total_seconds()*float(x)))
            # Adding nanosecond, if the time is zero:
            df['time'] = df['time'].apply(lambda x: datetime.timedelta(milliseconds=0.001) if x == 0 else x)
            df['date'] = self.start_time + df['time'].cumsum()
            self.df = df.set_index(self.df.index.names+['date'])
        if resample:
            if type(resample) in [str, unicode]:
                self.df = self.df.reset_index().set_index('date').resample(resample)
            else: # just some default resampling
                self.df = self.df.reset_index().set_index('date')
                duration = (self.df.index[-1]-self.df.index[0]).total_seconds()
                if 0 <= duration and duration <= 3600:
                    self.df.resample('1Min')
                if 3600 < duration and duration <= 86400:
                    self.df.resample('1H')
                if 86400 < duration and duration <= 432000:
                    self.df.resample('1D')
                if 432000 < duration and duration <= 12096000:
                    self.df.resample('1W')
                if 12096000 < duration and duration <= 47520000:
                    self.df.resample('1M')
                if 47520000 < duration:
                    self.df.resample('1A')
        if fill:
            if fill == 'interpolate':
                self.df = self.df.apply(pd.Series.interpolate)
            else:
                self.df = self.df.fillna(method='ffill')
        if cumsum:
            self.df['ivalue_sum'] = self.df['ivalue'].cumsum()
            self.df['ovalue_sum'] = self.df['ovalue'].cumsum()
            self.df['value_sum'] = self.df['value'].cumsum()
        if not silent:
            return self.df
    def plot(self, scenario='normal', dates=True, value=True, iweights=False, oweights=False, resample=True, fill=True, cumsum=True, legend=''):
        if not legend:
            legend = scenario+' scenario'
        if cumsum:
            self.to_df(scenario=scenario, dates=dates, value=value, iweights=iweights, oweights=oweights, resample=resample, fill=fill).rename(columns={'value': legend})[legend].cumsum().plot(legend=True)
        else:
            self.to_df(scenario=scenario, dates=dates, value=value, iweights=iweights, oweights=oweights, resample=resample, fill=fill).rename(columns={'value': legend})[legend].plot(legend=True)
    def plots(self, legend=''):
        self.plot(scenario="worst", legend=(legend+" (worst scenario)").strip())
        self.plot(scenario="normal", legend=(legend+" (normal scenario)").strip())
        self.plot(scenario="best", legend=(legend+" (best scenario)").strip())

class IdeaList(list):
    def _compute_data_frames(self):
        for i in range(list.__len__(self)):
            list.__getitem__(self, i).to_df(scenario='normal', dates=True, value=True, iweights=False, oweights=False, resample=True, fill=True, silent=True)
    def _compute_common_index(self):
        if list.__len__(self) <= 0:
            return False
        self.index = list.__getitem__(self,0).df.index
        for i in range(1,list.__len__(self)):
            self.index = self.index.union(list.__getitem__(self, i).df.index)
    def _reindex_data_frames(self):
        for i in range(list.__len__(self)):
            list.__getitem__(self, i).df = list.__getitem__(self, i).df.reindex(self.index)
    def align(self):
        self._compute_data_frames()
        self._compute_common_index()
        self._reindex_data_frames()
    def merge(self, variable='value'):
        self.df = pd.concat([list.__getitem__(self, i).df['value'] for i in range(list.__len__(self))],axis=1)
        self.df.columns = range(1,len(self.df.columns)+1) # just to correspond to idea natural number
    def plot(self, kind='default'):
        self.align()
        if kind == 'default':
            for i in range(list.__len__(self)):
                list.__getitem__(self, i).plot(legend='Idea %s (normal scenario)'%i, scenario='normal')
        if kind == 'value': # (currently buggy)
            self.merge()
            self.df.bfill().plot(linewidth=2)
    def plots(self):
        for i in range(list.__len__(self)):
            list.__getitem__(self, i).plots(legend='Idea %s'%i)

