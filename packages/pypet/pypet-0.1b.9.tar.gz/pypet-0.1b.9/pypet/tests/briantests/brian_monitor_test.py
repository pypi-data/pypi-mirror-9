from brian import SpikeCounter
from pypet.brian.parameter import BrianMonitorResult
from pypet.tests.parameter_test import ResultTest

__author__ = 'Robert Meyer'

from pypet.tests.briantests.run_a_brian_network import run_network
import pypet.utils.comparisons as comp
import brian

from brian.monitor import SpikeMonitor,SpikeCounter,StateMonitor, \
    PopulationSpikeCounter, PopulationRateMonitor, StateSpikeMonitor,  \
        MultiStateMonitor, ISIHistogramMonitor, VanRossumMetric, Monitor

from brian.fundamentalunits import Unit, Quantity, get_unit, get_unit_fast

from brian import clear



class BrianMonitorTest(ResultTest):

    @classmethod
    def setUpClass(cls):
        BrianMonitorResult.monitors=run_network()
        pass

    @classmethod
    def tearDownClass(cls):
        clear(True, True)
        reload(brian)

    def setUp(self):
        self.monitors = BrianMonitorResult.monitors
        self.make_results()
        self.make_constructor()


    def check_spike_counter(self, res, monitor):
        self.assertTrue(comp.nested_equal(monitor.count, res.count))
        self.assertTrue(comp.nested_equal(monitor.nspikes, res.nspikes))
        self.assertTrue(comp.nested_equal(str(monitor.source), res.source))

    def check_van_rossum_metric(self,res, monitor):
        self.assertTrue(comp.nested_equal(float(monitor.tau), res.tau))
        self.assertTrue(comp.nested_equal('second', res.tau_unit))
        self.assertTrue(comp.nested_equal(monitor.distance, res.distance))
        self.assertTrue(comp.nested_equal(monitor.N, res.N))
        self.assertTrue(comp.nested_equal(str(monitor.source), res.source))

    def check_population_spike_counter(self, res, monitor):
        self.assertTrue(comp.nested_equal(monitor.delay, res.delay))
        self.assertTrue(comp.nested_equal(monitor.nspikes, res.nspikes))
        self.assertTrue(comp.nested_equal(str(monitor.source), res.source))

    def check_state_spike_monitor(self, res, monitor):
        self.assertTrue(comp.nested_equal(monitor.delay, res.delay))
        self.assertTrue(comp.nested_equal(monitor.nspikes, res.nspikes))
        self.assertTrue(comp.nested_equal(str(monitor.source), res.source))
        self.assertTrue(comp.nested_equal(monitor._varnames, res.varnames))

        self.assertEqual('second', res.spiketimes_unit)

        if res.v_storage_mode == BrianMonitorResult.TABLE_MODE:
            spike_frame = res.spikes
            spiked_list=sorted(list(set(spike_frame['neuron'].to_dict().values())))
            self.assertEqual(spiked_list, res.neurons_with_spikes)
            for idx,val_tuple in enumerate(monitor.spikes):
                neuron = val_tuple[0]
                time = val_tuple[1]
                vals = val_tuple[2:]

                self.assertEqual(neuron, spike_frame['neuron'][idx])

                self.assertEqual(float(time), spike_frame['spiketimes'][idx])

                for idx_var, varname in enumerate(res.varnames):
                    val = vals[idx_var]
                    self.assertEqual(float(val),spike_frame[varname][idx])



        elif res.v_storage_mode == BrianMonitorResult.ARRAY_MODE:

            self.assertTrue('%0' in res.format_string and 'd' in res.format_string)

            spiked_set=set()
            for item_name in res:

                if item_name.startswith('spiketimes') and not item_name.endswith('unit'):
                    neuron_id = int(item_name.split('_')[-1])
                    spiked_set.add(neuron_id)

                    times = monitor.times(neuron_id)
                    self.assertTrue(comp.nested_equal(times,res[item_name]))

                for varname in res.varnames:
                    if item_name.startswith(varname) and not item_name.endswith('unit'):
                        neuron_id =int(item_name.split('_')[-1])
                        values = monitor.values(varname,neuron_id)


                        # Remove units:
                        self.assertTrue(comp.nested_equal(values,res[item_name]))

            spiked_list = sorted(list(spiked_set))
            self.assertEqual(spiked_list, res.neurons_with_spikes)
        else:
            raise RuntimeError('You shall not pass!')


        # Check Units
        for idx,varname in enumerate(monitor._varnames):
            unit = repr(get_unit_fast(monitor.spikes[0][idx+2]))
            self.assertTrue(unit,res[varname+'_unit'])


    def check_population_rate_monitor(self, res, monitor):
        self.assertEqual(str(monitor.source),res.source)
        self.assertTrue(comp.nested_equal(monitor._bin,res.bin))
        self.assertTrue(comp.nested_equal('second',res.times_unit))
        self.assertTrue(comp.nested_equal('Hz',res.rate_unit))
        self.assertTrue(comp.nested_equal(monitor.rate,res.rate))
        self.assertTrue(comp.nested_equal(monitor.times,res.times))
        self.assertTrue(comp.nested_equal(monitor.delay,res.delay))

    def check_isi_hist_monitor(self, res, monitor):
        self.assertEqual(str(monitor.source),res.source)
        self.assertTrue(comp.nested_equal(monitor.count,res.count))
        self.assertTrue(comp.nested_equal(monitor.bins,res.bins))
        self.assertTrue(comp.nested_equal(monitor.delay,res.delay))
        self.assertEqual(monitor.nspikes, res.nspikes)


    def check_spike_monitor(self, res, monitor):
        self.assertTrue(comp.nested_equal(monitor.delay, res.delay))
        self.assertTrue(comp.nested_equal(monitor.nspikes, res.nspikes))
        self.assertTrue(comp.nested_equal(str(monitor.source), res.source))


        self.assertEqual('second', res.spiketimes_unit)

        if res.v_storage_mode == BrianMonitorResult.TABLE_MODE:
            spike_frame = res.spikes
            spiked_list=sorted(list(set(spike_frame['neuron'].to_dict().values())))
            self.assertEqual(spiked_list, res.neurons_with_spikes)
            for idx,val_tuple in enumerate(monitor.spikes):
                neuron = val_tuple[0]
                time = val_tuple[1]
                vals = val_tuple[2:]

                self.assertEqual(neuron, spike_frame['neuron'][idx])

                self.assertEqual(float(time), spike_frame['spiketimes'][idx])


        elif res.v_storage_mode == BrianMonitorResult.ARRAY_MODE:

            self.assertTrue('%0' in res.format_string and 'd' in res.format_string)

            spiked_set=set()
            for item_name in res:

                if item_name.startswith('spiketimes') and not item_name.endswith('unit'):
                    neuron_id = int(item_name.split('_')[-1])
                    spiked_set.add(neuron_id)

                    times = monitor.spiketimes[neuron_id]
                    self.assertTrue(comp.nested_equal(times,res[item_name]))

            spiked_list = sorted(list(spiked_set))
            self.assertEqual(spiked_list, res.neurons_with_spikes)
        else:
            raise RuntimeError('You shall not pass!')

    def check_multi_state_monitor(self, res, monitor):
        self.assertEqual(monitor.vars, res.vars)

        if len(monitor.times)>0:
            self.assertEqual('second', res.times_unit)
            self.assertTrue(comp.nested_equal(monitor.times, res.times))




        for idx, varname in enumerate(monitor.vars):
            mon = monitor.monitors[varname]
            self.assertTrue(comp.nested_equal(mon.record, res.record))

            self.assertTrue(comp.nested_equal(mon.when, res.when))

            self.assertEqual(mon.timestep, res.timestep)
            self.assertTrue(comp.nested_equal(str(mon.P), res.source))

            if hasattr(res, varname+'_mean'):
                self.assertTrue(comp.nested_equal(mon.mean, res.f_get(varname+'_mean')))
                self.assertTrue(comp.nested_equal(mon.var, res.f_get(varname+'_var')))
            if len(monitor.times)>0:
                self.assertTrue(comp.nested_equal(mon.values, res.f_get(varname+'_values')))

            self.assertTrue(comp.nested_equal(repr(mon.unit), res.f_get(varname+'_unit')))


    def check_state_monitor(self, res, monitor):

        self.assertEqual('second', res.times_unit)
        self.assertEqual(monitor.varname, res.varname)
        self.assertEqual(repr(monitor.unit), res.unit)
        self.assertTrue(comp.nested_equal(monitor.record, res.record))

        self.assertTrue(comp.nested_equal(monitor.when, res.when))

        self.assertEqual(monitor.timestep, res.timestep)
        self.assertTrue(comp.nested_equal(str(monitor.P), res.source))

        if hasattr(res, 'mean'):
            self.assertTrue(comp.nested_equal(monitor.mean, res.mean))
            self.assertTrue(comp.nested_equal(monitor.var, res.var))

        if len(monitor.times) > 0:
            self.assertTrue(comp.nested_equal(monitor.times, res.times))
            self.assertTrue(comp.nested_equal(monitor.values, res.values))


    def test_failing_adding_another_monitor_or_changing_the_mode(self):

        for res in self.results.values():
            with self.assertRaises(TypeError):
                res.f_set(monitor=self.monitors.values()[0])

        for res in self.results.values():
            with self.assertRaises(TypeError):
                res.v_storage_mode=BrianMonitorResult.ARRAY_MODE

    def test_the_insertion_made_implicetly_in_setUp(self):

        for key,monitor in self.monitors.items():
            res = self.results[key]
            self.assertEqual(res.testtestextra,42)
            self.assertEqual(res.v_monitor_type,monitor.__class__.__name__)

            if isinstance(monitor, SpikeCounter):
                self.check_spike_counter(res, monitor)

            elif isinstance(monitor, VanRossumMetric):
                self.check_van_rossum_metric(res, monitor)

            elif isinstance(monitor, PopulationSpikeCounter):
                self.check_population_spike_counter(res, monitor)

            elif isinstance(monitor, StateSpikeMonitor):
                self.check_state_spike_monitor(res, monitor)

            elif  isinstance(monitor, PopulationRateMonitor):
                self.check_population_rate_monitor(res, monitor)


            elif isinstance(monitor, ISIHistogramMonitor):
                self.check_isi_hist_monitor(res, monitor)

            elif isinstance(monitor,SpikeMonitor):
                self.check_spike_monitor(res, monitor)

            elif isinstance(monitor, MultiStateMonitor):
                self.check_multi_state_monitor(res, monitor)

            elif isinstance(monitor,StateMonitor):
                self.check_state_monitor(res, monitor)


            else:
                raise ValueError('Monitor Type %s is not supported (yet)' % str(type(monitor)))

    def test_dir(self):
        res = self.results['SpikeMonitor']
        self.assertTrue('spikes' in res)
        self.assertTrue('spikes' in dir(res))

    def test_set_item_via_number(self):
        res = self.results['SpikeMonitor']
        res[0] = 'Hi'
        res[777] = 777

        self.assertTrue(getattr(res, res.v_name) == 'Hi')
        self.assertTrue(res.f_get(0) == 'Hi')
        self.assertTrue(getattr(res, res.v_name + '_777') == 777)
        self.assertTrue(res[777] == 777)
        self.assertTrue(res.f_get(777) == 777)

        self.assertTrue(0 in res)
        self.assertTrue(777 in res)
        self.assertTrue(99999999 not in res)

        del res[0]
        self.assertTrue(0 not in res)

        del res[777]
        self.assertTrue(777 not in res)

    def make_results(self):
        self.results={}
        for key,monitor in self.monitors.items():
            if key.endswith('Ar'):
                self.results[key]=BrianMonitorResult(key,monitor,
                                                     storage_mode=BrianMonitorResult.ARRAY_MODE)
            else:
                self.results[key]=BrianMonitorResult(key,monitor)

            self.results[key].f_set(testtestextra=42)

