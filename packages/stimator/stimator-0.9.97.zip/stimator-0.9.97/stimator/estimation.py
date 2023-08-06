# -*- coding:utf8 -*-

import de
from numpy import array, nansum, fabs, copy, empty, linspace, isnan
import math
from scipy import integrate
from dynamics import getdXdt, init2array
import fim
import timecourse
import matplotlib as mpl
from matplotlib import pylab as pl
import seaborn as sns
## try:
##     import seaborn as sns
## except ImportError:
##     import smallseaborn as sns

# ----------------------------------------------------------------------------
#         Class to perform DE optimization for ODE systems
# ----------------------------------------------------------------------------

def _repeatitems(sequence, repetitions):
    newlist = []
    for x in sequence:
        newlist.extend([x] * repetitions)
    return newlist

class OptimumData(object):
    """Object that holds optimum solution data."""

    def __init__(self, optimizer):
        self.optimizer = optimizer

    def info(self):
        optimum = self
        headerformat = "--- %-20s -----------------------------\n"
        res = "\n" + (headerformat % 'PARAMETERS')
        res += "\n".join(["%s\t%12g +- %g" % i for i in optimum.parameters])
        res += '\n\n'
        res += headerformat % 'OPTIMIZATION'
        res += "%s\t%g\n" % ('Final Score', optimum.optimization_score)
        res += "%s\t%d\n" % ('generations', optimum.optimization_generations)

        res += "%s\t%d\n" % ('max generations', optimum.max_generations)
        res += "%s\t%d\n" % ('population size', optimum.pop_size)
        res += "%s\t%s\n" % ('Exit by',     optimum.optimization_exit_by)
        res += '\n\n'

        res += headerformat % 'TIME COURSES'
        res += '\t\t'.join(['Name', 'Points', 'Score'])+'\n'
        res += "\n".join(["%s\t%d\t%g" % i for i in optimum.tcdata])
        res += '\n\n'
        return res

    def print_info(self):
        print (self.info())

    def plot(self, figure=None, 
             axis_set=None,
             fig_size=None,
             context=None, 
             style=None, 
             palette=None,
             font="sans-serif", 
             font_scale=1,
             save2file=None,
             show=False):

        curr_axes_style = sns.axes_style()
        curr_plotting_context = sns.plotting_context()
        curr_color_palette = sns.color_palette()
        original_figsize = tuple(mpl.rcParams['figure.figsize'])

        if context is not None:
            sns.set_context(context, font_scale, rc={"figure.figsize": fig_size})
        if style is not None:
            sns.set_style(style, rc={"font.family": font})
        if palette is not None:
            sns.set_palette(palette)
        
        if fig_size is not None:
            mpl.rcParams['figure.figsize'] = fig_size

        if axis_set is None:
            if figure is None:
                figure = pl.figure()

        original_cycle = mpl.rcParams["axes.color_cycle"]
        curr_cycle = _repeatitems(original_cycle, 2)
        mpl.rcParams["axes.color_cycle"] = curr_cycle
        
##         s = timecourse.Solutions()
##         
##         for sol in self.optimum_dense_tcs:
##             s += sol
##         
##         s.plot(figure=figure, show=show, force_dense=True)
##         mpl.rcParams["axes.color_cycle"] = original_cycle
##         return

        bestsols = self.optimum_dense_tcs
        expsols = self.optimizer.tc
        tcstats = self.tcdata
        ntc = len(bestsols)
        ncols = int(math.ceil(math.sqrt(ntc)))
        nrows = int(math.ceil(float(ntc)/ncols))
        if axis_set is None:
            axis_set = [figure.add_subplot(nrows, ncols,i+1) for i in range(ntc)]
        else:
            axis_set = axis_set
        
        for i in range(ntc):
            subplot = axis_set[i]
            # subplot.set_xlabel("time")
            subplot.set_title("%s (%d pt) %g" % tcstats[i], fontsize=12)
            expsol = expsols[i]
            symsol = bestsols[i]

            for line in range(len(expsol)):
                # count NaN and do not plot if they are most of the timecourse
                yexp = expsol[line]
                nnan = len(yexp[isnan(yexp)])
                if nnan >= expsol.ntimes-1:
                    continue
                # otherwise plot lines
                xname = expsol.names[line]
                ysim = symsol[symsol.names.index(xname)]
                lsexp, mexp = 'None', 'o'
                lssim, msim = '-', 'None'
                subplot.plot(expsol.t, yexp, marker=mexp, ls=lsexp)
                subplot.plot(symsol.t, ysim, marker=msim, ls=lssim,
                             label='%s' % xname)
            subplot.legend(loc='best')

        if save2file is not None:
            figure.savefig(save2file)
        if show:
            if save2file is not None:
                if hasattr(save2file,'read'):
                    save2file.close()
            pl.show()

        # restore seaborn styles
        sns.set_context(curr_plotting_context)
        sns.set_style(curr_axes_style)
        sns.set_palette(curr_color_palette)
        mpl.rcParams['figure.figsize'] = original_figsize
        mpl.rcParams["axes.color_cycle"] = original_cycle

    def plot_generations(self, generations = None,
                         pars = None,
                         figure=None, show=False):
        if not self.generations_exist:
            raise IOError('file generations.txt was not generated')

        if figure is None:
            figure = pl.figure()
        figure.clear()

        if generations is None:
            all_gens = range(self.optimization_generations +1)
            dump_generations = all_gens

        n_gens = len(dump_generations)
        
        if pars is None:
            first2 = self.parameters[:2]
            pars = [p[0] for p in first2]
        
        pnames = [p[0] for p in self.parameters]
        
        colp0 = pnames.index(pars[0])
        colp1 = pnames.index(pars[1])
        
        scores_col = len(self.parameters)
        
        ax1 = pl.subplot(1,2,1)
        ax2 = pl.subplot(1,2,2)
        # parse generations
        gen = -1
        f = open('generations.txt')
        solx = []
        soly = []
        objx = []
        objy = []
        reading = False
        for line in f:
            line = line.strip()
            if line == '' and reading:
                if len(solx) > 0:
                    ax1.plot(solx, soly, marker='o', ls='None', label=gen)
                    ax2.plot(objx, objy, marker='o', ls='None', label=gen)
                    solx = []
                    soly = []
                    objx = []
                    objy = []
                    reading = False
            elif line.startswith('generation'):
                gen = line.split()[1]
                igen = int(gen)
                if igen in dump_generations:
                    reading = True
                    # print 'generation', gen
            elif reading:
                line = [float(x) for x in line.split()]
                solx.append(line[colp0])
                soly.append(line[colp1])
                objx.append(igen)
                objy.append(line[scores_col])
            else:
                continue
        f.close()
        ax1.legend(loc=0)
        ax1.set_title('population')
        ax1.set_xlabel(pars[0])
        ax1.set_ylabel(pars[1])
        ax2.set_title('scores')
        ax2.set_yscale('log')
        ax2.set_xlabel('generation')
        if show:
            pl.show()

class DeODEOptimizer(de.DESolver):
    """Overides energy function and report functions.

    The energy function solves ODEs and computes a least-squares score.
    Ticker functions are called on completion of a generation and when
    optimization finishes.
    """

    def __init__(self, model, optSettings, tcs, weights=None,
                 aMsgTicker=None,
                 anEndComputationTicker=None,
                 dump_generations=None,
                 dump_predictions=False,
                 initial='init',
                 maxGenerations_noimprovement=20):
        self.model = model
        self.tc = tcs
        self.varnames = model.varnames
        self.endTicker = anEndComputationTicker
        self.msgTicker = aMsgTicker
        self.dump_predictions = dump_predictions
        self.dump_generations = dump_generations

        # reorder variables according to model
        self.tc.orderByModelVars(self.model)

        pars = model.with_bounds
        mins = array([u.bounds.lower for u in pars])
        maxs = array([u.bounds.upper for u in pars])

        if optSettings.get('pop_size', None) is None:
            optSettings['pop_size'] = optSettings['genomesize']
        if optSettings.get('max_generations', None) is None:
            optSettings['max_generations'] = optSettings['generations']

        de.DESolver.__init__(self, len(pars),  # number of parameters
                             int(optSettings['pop_size']),  # pop size
                             int(optSettings['max_generations']),  # max gens
                             mins, maxs,  # min and max parameter values
                             "Best2Exp",  # DE strategy
                             0.7, 0.6,  # DiffScale, Crossover Prob
                             0.0,  # Cut-off energy
                             True,  # use class random-number methods
                             maxGenerations_noimprovement)

        # cutoffEnergy is 1e-6 of deviation from data
        self.cutoffEnergy = 1.0e-6 * sum([nansum(fabs(tc.data)) for tc in self.tc])

        # scale times to maximum time in data
        scale = float(max([(tc.t[-1]-tc.t[0]) for tc in self.tc]))
        t0 = self.tc[0].t[0]

        self.calcDerivs = getdXdt(model,
                                  scale=scale,
                                  with_uncertain=True,
                                  t0=t0)
        self.salg = integrate._odepack.odeint

        # store initial values and (scaled) time points
        if isinstance(initial, str) or isinstance(initial, StateArray):
            try:
                globalX0 = copy(init2array(model))
            except AttributeError:
                globalX0 = zeros(len(model.varnames))

        else:
            globalX0 = copy(initial)

        self.X0 = []
        self.times = []
        for data in self.tc:
            X0 = []
            for ix, xname in enumerate(model.varnames):
                if xname in data.names:
                    X0.append(data[xname][0])
                else:
                    X0.append(globalX0[ix])
            X0 = array(X0, dtype=float)

            self.X0.append(X0)
            t = data.t
            times = (t-t0)/scale  # +t0  # this scales time points
            self.times.append(times)
        self.timecourse_scores = empty(len(self.tc))

        # find uncertain initial values
        mapinit2trial = []
        for iu, u in enumerate(self.model.with_bounds):
            if u.name.startswith('init'):
                varname = u.name.split('.')[-1]
                ix = self.varnames.index(varname)
                mapinit2trial.append((ix, iu))
        self.trial_initindexes = array([j for (i, j) in mapinit2trial], dtype=int)
        self.vars_initindexes = array([i for (i, j) in mapinit2trial], dtype=int)

        self.criterium = timecourse.getCriteriumFunction(weights,
                                                         self.model,
                                                         self.tc)

    def computeSolution(self, i, trial, dense=None):
        """Computes solution for timecourse i, given parameters trial."""

        y0 = copy(self.X0[i])
        # fill uncertain initial values
        y0[self.vars_initindexes] = trial[self.trial_initindexes]
        if dense is None:
            ts = self.times[i]
        else:
            ts = linspace(self.times[i][0], self.times[i][-1], 500)
        output = self.salg(self.calcDerivs, y0, ts, (), None, 0, -1, -1, 0,
                           None, None, None, 0.0, 0.0, 0.0, 0, 0, 0, 12, 5)
        if output[-1] < 0:
            return None
        # if infodict['message'] != 'Integration successful.':
        #     return (1.0E300)
        return output[0]

    def externalEnergyFunction(self, trial):
        # if out of bounds flag with error energy
        for trialpar, minInitialValue, maxInitialValue in zip(trial, self.minInitialValue, self.maxInitialValue):
            if trialpar > maxInitialValue or trialpar < minInitialValue:
                return 1.0E300
        # set parameter values from trial
        self.model.set_uncertain(trial)

        # compute solutions and scores
        for i in range(len(self.tc)):
            Y = self.computeSolution(i, trial)
            if Y is not None:
                self.timecourse_scores[i] = self.criterium(Y, i)
            else:
                return (1.0E300)

        globalscore = self.timecourse_scores.sum()
        return globalscore

    def reportInitial(self):
        msg = "\nSolving %s..." % self.model.metadata.get('title', '')
        if self.dump_generations is not None:
            self.dumpfile = open('generations.txt', 'w')
        if not self.msgTicker:
            print msg
        else:
            self.msgTicker(msg)

    def reportGeneration(self):
        msg = "%-4d: %f" % (self.generation, float(self.bestEnergy))
        if not self.msgTicker:
            print msg
        else:
            self.msgTicker(msg)
        if self.dump_generations is not None:
            print >> self.dumpfile, self.generation_string(self.generation)

    def reportFinal(self):
        if self.exitCode <= 0:
            outCode = -1
        else:
            outCode = self.exitCode
            self.generateOptimumData()
        if not self.endTicker:
            print self.reportFinalString()
        else:
            self.endTicker(outCode)
        if self.dump_generations is not None:
            print >> self.dumpfile, self.generation_string(self.generation)
            self.dumpfile.close()

    def generation_string(self, generation):
        generation = str(generation)
        # find if objectives is iterable
        isiter = hasattr(self.popEnergy[0], '__contains__')
        res = 'generation %s -------------------------\n' % generation
        for s, o in zip(self.population, self.popEnergy):
            sstr = ' '.join([str(i) for i in s])
            if isiter:
                ostr = ' '.join([str(i) for i in o])
            else:
                ostr = str(o)
            res = res + '%s %s\n' % (sstr, ostr)
        return res

    def generateOptimumData(self):
        # compute parameter standard errors, based on FIM-1
        # generate TC solutions
        best = OptimumData(self)
        best.optimization_score = self.bestEnergy
        best.optimization_generations = self.generation
        best.optimization_exit_by = self.exitCodeStrings[self.exitCode]
        best.max_generations = self.maxGenerations
        best.pop_size = self.populationSize

        # TODO: Store initial solver parameters?

        # generate best time-courses

        # par_names = [self.model.with_bounds[i].name for i in range(len(self.bestSolution))]
        par_names = [p.name for p in self.model.with_bounds]
        parameters = zip(par_names, [x for x in self.bestSolution])

        sols = timecourse.Solutions()
        best.tcdata = []

        for (i, tc) in enumerate(self.tc):
            Y = self.computeSolution(i, self.bestSolution)
            if Y is not None:
                score = self.criterium(Y, i)
            else:
                score = 1.0E300
            sol = timecourse.SolutionTimeCourse(tc.t,
                                                Y.T,
                                                self.varnames,
                                                title=tc.title)
            sols += sol
            best.tcdata.append((self.tc[i].title, tc.ntimes, score))

        best.optimum_tcs = sols

        if not (fim.sympy_installed):
            best.parameters = [(p, v, 0.0) for (p, v) in parameters]
        else:
            commonvnames = timecourse.getCommonFullVars(self.tc)
            consterror = timecourse.getRangeVars(self.tc, commonvnames)
            # assume 5% of range
            consterror = timecourse.constError_func([r * 0.05 for r in consterror])
            FIM1, invFIM1 = fim.computeFIM(self.model,
                                           parameters,
                                           sols,
                                           consterror,
                                           commonvnames)
            best.parameters = [(par_names[i], value, invFIM1[i, i]**0.5) for (i, value) in enumerate(self.bestSolution)]

        sols = timecourse.Solutions()
        for (i, tc) in enumerate(self.tc):
            Y = self.computeSolution(i, self.bestSolution, dense=True)
            ts = linspace(tc.t[0], tc.t[-1], 500)

            sol = timecourse.SolutionTimeCourse(ts,
                                                Y.T,
                                                self.varnames,
                                                title=tc.title)
            sols += sol

        best.optimum_dense_tcs = sols

        if self.dump_generations is not None:
            best.generations_exist = True
        else:
            best.generations_exist = False

        self.optimum = best
        # self.generate_fitted_sols()

        if self.dump_predictions:
            fnames = ['pred_' + self.tc[i].title for i in range(len(self.tc))]
            best.optimum_tcs.saveTimeCoursesTo(fnames, verbose=True)


def s_timate(model, timecourses=None, opt_settings=None,
             tc_dir=None,
             intvarsorder=None,
             names=None,
             verbose_readingTCs=True,
             **kwargs):

    # create a default dict of optimizer settings,
    # then update with .metadata['optSettings']
    # finally, update with argument opt_settings
    optSettings = {'pop_size': 80,
                   'max_generations': 200,
                   'optimizer': 'DeODEOptimizer'}
    if model.metadata.get('optSettings', None) is not None:
        optSettings.update(model.metadata['optSettings'])
    if opt_settings is not None:
        optSettings.update(opt_settings)

    # timecourses argument is used to indicate time-course files
    # if it is None, then use model.metadata['timecourses']
    if timecourses is None:
        timecourses = model  # use model as source in readTCs

    tcs = timecourse.readTCs(timecourses,
                             filedir=tc_dir,
                             intvarsorder=intvarsorder,
                             names=names,
                             verbose=verbose_readingTCs)

    optimizer = DeODEOptimizer(model, optSettings, tcs, **kwargs)
    optimizer.run()
    return optimizer.optimum


def test():
    from modelparser import read_model
    m1 = read_model("""
title Glyoxalase system in L. Infantum

glx1 : HTA -> SDLTSH, V1*HTA/(Km1 + HTA)
#glx1 : HTA -> SDLTSH, V*HTA/(Km1 + HTA), V=2.57594e-05
glx2 : SDLTSH ->,     V2*SDLTSH/(Km2 + SDLTSH)

#find glx1.V  in [0.00001, 0.0001]
find V1  in [0.00001, 0.0001]

Km1 = 0.252531
find Km1 in [0.01, 1]

V2  = 2.23416e-05
find V2 in [0.00001, 0.0001]

Km2 = 0.0980973
find Km2 in (0.01, 1)

init : (SDLTSH = 7.69231E-05, HTA = 0.1357)

timecourse TSH2a.txt
timecourse TSH2b.txt
""")

    # print m1

    optimum = s_timate(m1, tc_dir='examples/timecourses', 
                       names=['SDLTSH', 'HTA'],
                       dump_generations=True) 
    # maxGenerations_noimprovement=40)
    # ... intvarsorder=(0,2,1) ...

    optimum.print_info()
    optimum.plot()
    optimum.plot_generations(pars=['V2', 'Km1'])

    # --- an example with unknown initial values --------------------

    m2 = m1.copy()

    # Now, assume init.HTA is uncertain
    m2.set_bounds('init.HTA', (0.05, 0.25))
    # do not estimate Km1 and Km2, to help the analysis
    m2.reset_bounds('Km1')
    m2.reset_bounds('Km2')

    # VERY IMPORTANT:
    # only one time course can be used:
    # cannot fit one initial value using several timecourses!!!

    optimum = s_timate(m2, timecourses=['TSH2a.txt'], 
                       tc_dir='examples/timecourses',
                       opt_settings={'pop_size': 60},
                       names=['SDLTSH', 'HTA'])

    optimum.print_info()
    optimum.plot(show=True)

if __name__ == "__main__":
    test()
