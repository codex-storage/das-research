import time
import progressbar
import random
import numpy as np
import pandas as pd
import dht
from utils import getStrFromDelayRange

TOTAL_PERCENTAGE = 100
PERCENTAGE_INTERVALS = 1


class SingleDHTretrievalStudy:

    def __init__(self, csvFolder, imgFolder, jobs, nn, rn, samples,
                 fErrR, sErrR, cDelR, fDelR, sDelR, k, a, b, y, stepsToStop):
        self.csvFolder = csvFolder
        self.imgFolder = imgFolder
        self.jobs = jobs
        self.nn = nn
        self.rn = rn
        self.samples = samples
        self.fastErrorRate = fErrR
        self.slowErrorRate = sErrR
        self.connDelayRange = cDelR
        self.fastDelayRange = fDelR
        self.slowDelayRange = sDelR  # timeouts
        self.k = k
        self.alpha = a
        self.beta = b
        self.gamma = y
        self.stepsToStop = stepsToStop
        # namings
        s = ""
        s += f"_nn{nn}"
        s += f"_rn{rn}"
        s += f"_sampl{samples}"
        s += f"_fer{fErrR}"
        s += f"_ser{sErrR}"
        s += f"_cdr{getStrFromDelayRange(cDelR)}"
        s += f"_fdr{getStrFromDelayRange(fDelR)}"
        s += f"_sdr{getStrFromDelayRange(sDelR)}"
        s += f"_k{k}"
        s += f"_a{a}"
        s += f"_b{b}"
        s += f"_y{y}"
        s += f"_steps{stepsToStop}"
        self.studyName = s
        print(f"Retrieval Study => {s}")

    def run(self):
        # Init the DHT Network
        testInitTime = time.time()
        network = dht.DHTNetwork(
            0,
            self.fastErrorRate,
            self.slowErrorRate,
            self.connDelayRange,
            self.fastDelayRange,
            self.slowDelayRange,
            self.gamma)
        initStartTime = time.time()
        network.init_with_random_peers(
            self.jobs,
            self.nn,
            self.k,
            self.alpha,
            self.beta,
            self.stepsToStop)
        self.networkInitTime = time.time() - initStartTime
        print(f"network init done in {self.networkInitTime} secs")

        # get random node to propose publish the
        builderNode = network.nodestore.get_node(random.randint(0, self.nn))

        # create and publish @@@ number of samples to the network
        # lookups metrics
        ks = []
        nns = []
        stepstostops = []
        fastErrorRate = []
        slowErrorRate = []
        connDelayRange = []
        fastDelayRange = []
        slowDelayRange = []
        alphas = []
        betas = []
        gammas = []
        providers = []
        sampleNames = []
        provideLookupAggrTime = []
        provideAggrTime = []
        provideOperationAggrTime = []
        provideSuccNodes = []
        provideFailedNodes = []
        samples = []

        for i in range(self.samples):
            sampleContent = f"sample {i}"
            summary, _ = builderNode.provide_block_segment(sampleContent)
            samples.append((sampleContent, sampleContent, summary))
            # add metrics for the csv
            ks.append(self.k)
            alphas.append(self.alpha)
            betas.append(self.beta)
            gammas.append(self.gamma)
            nns.append(self.nn)
            stepstostops.append(self.stepsToStop)
            fastErrorRate.append(f"{self.fastErrorRate}")
            slowErrorRate.append(f"{self.slowErrorRate}")
            connDelayRange.append(f"{getStrFromDelayRange(self.connDelayRange)}")
            fastDelayRange.append(f"{getStrFromDelayRange(self.fastDelayRange)}")
            slowDelayRange.append(f"{getStrFromDelayRange(self.slowDelayRange)}")
            providers.append(builderNode.ID)
            sampleNames.append(sampleContent)
            provideLookupAggrTime.append(summary['lookupDelay'])
            provideAggrTime.append(summary['provideDelay'])
            provideOperationAggrTime.append(summary['operationDelay'])
            provideSuccNodes.append(len(summary['succesNodeIDs']))
            provideFailedNodes.append(len(summary['failedNodeIDs']))

        # save the provide data
        df = pd.DataFrame({
            "number_nodes": nns,
            "k": ks,
            "alpha": alphas,
            "beta": betas,
            "gamma": gammas,
            "stop_steps": stepstostops,
            "fast_error_rate": fastErrorRate,
            "slow_error_rate": slowErrorRate,
            "connection_delay_range": connDelayRange,
            "fast_delay_range": fastDelayRange,
            "slow_delay": slowDelayRange,
            "provider": providers,
            "sample": sampleNames,
            "provide_lookup_aggr_time": provideLookupAggrTime,
            "provide_aggr_time": provideAggrTime,
            "provide_operation_aggr_time": provideOperationAggrTime,
            "provide_succ_nodes": provideSuccNodes,
            "provide_fail_nodes": provideFailedNodes,
        })

        df.to_csv(self.csvFolder + f"/retrieval_provide{self.studyName}.csv")
        network.reset_network_metrics()
        del df

        nns = []
        ks = []
        alphas = []
        betas = []
        gammas = []
        stepstostops = []
        fastErrorRate = []
        slowErrorRate = []
        connDelayRange = []
        fastDelayRange = []
        slowDelayRange = []
        retrievers = []
        sampleNames = []
        lookupTimes = []
        lookupAggrDelays = []
        attemptedNodes = []
        finishedConnAttempts = []
        successfullCons = []
        failedCons = []
        valRetrievable = []
        totalDiscNodes = []
        accuracies = []

        bar = progressbar.ProgressBar(
            maxval=self.rn,
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for i in range(self.rn):
            retrieverNode = network.nodestore.get_node(random.randint(0, self.nn))
            while retrieverNode.ID == builderNode.ID:
                retrieverNode = network.nodestore.get_node(random.randint(0, self.nn))

            for l in range(self.samples):
                sampleContent = f"sample {l}"
                sh = dht.Hash(sampleContent)
                lstime = time.time()
                closest, val, summary, aggrDelay = retrieverNode.lookup_for_hash(
                    key=sh, trackaccuracy=True, finishwithfirstvalue=True)
                lduration = time.time() - lstime

                if val == sampleContent:
                    valRetrievable.append(1)
                else:
                    valRetrievable.append(0)

                nns.append(self.nn)
                ks.append(self.k)
                alphas.append(self.alpha)
                betas.append(self.beta)
                gammas.append(self.gamma)
                stepstostops.append(self.stepsToStop)
                fastErrorRate.append(f"{self.fastErrorRate}")
                slowErrorRate.append(f"{self.slowErrorRate}")
                connDelayRange.append(f"{getStrFromDelayRange(self.connDelayRange)}")
                fastDelayRange.append(f"{getStrFromDelayRange(self.fastDelayRange)}")
                slowDelayRange.append(f"{getStrFromDelayRange(self.slowDelayRange)}")
                retrievers.append(retrieverNode.ID)
                sampleNames.append(sampleContent)
                lookupTimes.append(lduration)
                lookupAggrDelays.append(aggrDelay)
                finishedConnAttempts.append(summary['connectionFinished'])
                attemptedNodes.append(summary['connectionAttempts'])
                successfullCons.append(summary['successfulCons'])
                failedCons.append(summary['failedCons'])
                totalDiscNodes.append(summary['totalNodes'])
                accuracies.append(summary['accuracy'])

            # clean up the memory
            del sh
            del summary
            del closest

            # percentajes
            bar.update(i + 1)

        bar.finish()

        testDuration = time.time() - testInitTime
        print(f"test done in {testDuration} secs")
        print(f"DHT fast-init jobs:{self.jobs} done in {self.networkInitTime} secs")
        print(f"{self.nn} nodes, k={self.k}, alpha={self.alpha}, {len(lookupTimes)} lookups")
        print(f"mean time per lookup  : {np.mean(lookupTimes)}")
        print(f"mean aggr delay (secs): {np.mean(lookupAggrDelays) / 1000}")
        print(f"mean contacted nodes: {np.mean(attemptedNodes)}")
        print(f"time to make {len(lookupTimes)} lookups: {np.sum(lookupTimes)} secs")
        print()

        # Create the panda objs and export the to csvs
        df = pd.DataFrame({
            "number_nodes": nns,
            "k": ks,
            "alpha": alphas,
            "beta": betas,
            "gamma": gammas,
            "stop_steps": stepstostops,
            "fast_error_rate": fastErrorRate,
            "slow_error_rate": slowErrorRate,
            "connection_delay_range": connDelayRange,
            "fast_delay_range": fastDelayRange,
            "slow_delay": slowDelayRange,
            "retriever": retrievers,
            "sample": sampleNames,
            "lookup_wallclock_time": lookupTimes,
            "lookup_aggregated_delay": lookupAggrDelays,
            "attempted_nodes": attemptedNodes,
            "finished_connection_attempts": finishedConnAttempts,
            "successful_connections": successfullCons,
            "failed_connections": failedCons,
            "total_discovered_nodes": totalDiscNodes,
            "retrievable": valRetrievable,
            "accuracy": accuracies,
        })
        df.to_csv(self.csvFolder + f"/retrieval_lookup{self.studyName}.csv")

        # save the network metrics
        networkMetrics = network.connection_metrics()
        network_df = pd.DataFrame(networkMetrics)
        network_df.to_csv(self.csvFolder + f"/retrieval_lookup_network{self.studyName}.csv")

        del network
        del df
        del network_df
