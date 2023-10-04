import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from IPython.display import display

# Tag Identifiers
RETRIEVAL = "retrieval"
LOOKUP = "lookup"
NETWORK = "network"
NN = "nn"
RN = "rn"
SAMPL = "sampl"
FER = "fer"
SER = "ser"
CDR = "cdr"
FDR = "fdr"
SDR = "sdr"
K = "k"
A = "a"
B = "b"
Y = "y"
STEPS = "steps"
# --
OPERATION = "operation"
NUMBER_NODES = "number_nodes"
RETRIEVAL_NODES = "retrieval_nodes"
CONCURRENT_SAMPLES = "concurrent_samples"
FAST_ERROR_RATE = "fast_error_rate"
SLOW_ERROR_RATE = "slow_error_rate"
CONNECTION_DELAYS = "connection_delays"
FAST_ERROR_DELAYS = "fast_error_delays"
SLOW_ERROR_DELAYS = "slow_error_delays"
K_PARAMETER = "k_replication"
ALPHA = "alpha"
BETA = "beta"
GAMMA = "overhead"
STEPS_TO_STOP = "steps_to_stop"


# Utils
tag_example = "retrieval_lookup_nn12000_rn1_sampl100_fer10_ser0_cdr50-75_fdr50-100_sdr0_k20_a3_b20_y1.0_steps3"
def tag_parser(tag: str):
    params = {
        OPERATION: "",
        NUMBER_NODES: "",
        RETRIEVAL_NODES: "",
        CONCURRENT_SAMPLES: "",
        FAST_ERROR_RATE: "",
        SLOW_ERROR_RATE: "",
        CONNECTION_DELAYS: "",
        FAST_ERROR_DELAYS: "",
        SLOW_ERROR_DELAYS: "",
        K_PARAMETER: "",
        ALPHA: "",
        BETA: "",
        GAMMA: "",
        STEPS_TO_STOP: "",
    }
    # split the tag into - type & parameters
    raw_params = tag.split("_")
    for param in raw_params:
        if NN in param:
            params[NUMBER_NODES] = param.replace(NN, "")
        elif RN in param:
            params[RETRIEVAL_NODES] = param.replace(RN, "")
        elif SAMPL in param:
            params[CONCURRENT_SAMPLES] = param.replace(SAMPL, "")
        elif FER in param:
            params[FAST_ERROR_RATE] = param.replace(FER, "")
        elif SER in param:
            params[SLOW_ERROR_RATE] = param.replace(SER, "")
        elif CDR in param:
            params[CONNECTION_DELAYS] = param.replace(CDR, "")
        elif FDR in param:
            params[FAST_ERROR_DELAYS] = param.replace(FDR, "")
        elif SDR in param:
            params[SLOW_ERROR_DELAYS] = param.replace(SDR, "")
        elif K in param and param != "lookup":
            params[K_PARAMETER] = param.replace(K, "")
        elif A in param:
            params[ALPHA] = param.replace(A, "")
        elif B in param:
            params[BETA] = param.replace(B, "")
        elif Y in param:
            params[GAMMA] = param.replace(Y, "")
        elif STEPS in param:
            params[STEPS_TO_STOP] = param.replace(STEPS, "")
        else:
            if params[OPERATION] == "":
                params[OPERATION] = param
            else:
                params[OPERATION] += f"_{param}"
    return params

def compose_legend(params, labels):
    legend = ""
    for label in labels:
        if legend == "":
            legend = f"{label}={params[label]}"
        else:
            legend += f" {label}={params[label]}"
    return legend

def make_folder(folder, reason):
    try:
        os.mkdir(folder)
        print(f"created folder {folder} for {reason}")
    except FileExistsError:
        print(f"folder {folder} was already created")
    except Exception as e:
        print(e)


# --- Single Metrics ---
class SingleMetrics:

    metrics = {
        "lookup_aggregated_delay": {
            "title_tag": "delay",
            "xlabel_tag": "delay (ms)",
            "ylabel_tag": "",
        },
        "finished_connection_attempts": {
            "title_tag": "hops",
            "xlabel_tag": "hops",
            "ylabel_tag": "",
        },
        "accuracy": {
            "title_tag": "accuracy",
            "xlabel_tag": "accuracy",
            "ylabel_tag": "",
        },
    }

    def __init__(self, file, output_image_folder, operation, metrics: dict = dict()):
        self.file = file
        self.df = pd.read_csv(file)
        self.label = file.split("/")[-1].replace(".csv", "")
        self.targetFolder = output_image_folder+"/"+self.label
        self.operation = operation
        # add metrics to pre-existing ones
        self.metrics.update(metrics)
        # Make sure there is a valid folder for the imgaes
        make_folder(self.targetFolder, f"for keeping the lookup related images about {self.label}\n")
        print(f"plotting {self.label}, saving figures at {self.targetFolder}\n")
        # display the lookup wallclock cdf

        # display the aggregated delay cdf
        for metric_name, metric_opts in self.metrics.items():
            self.plot_cdf(metric_name, metric_opts)
            self.plot_pdf(metric_name, metric_opts)

    def plot_cdf(self, column_name, column_opts):
        df = self.df.sort_values(column_name)
        # CDF
        sns.set()
        g = sns.lineplot(data=df, x=column_name, y=np.linspace(0, 1, len(df)), color='red', ci=None)
        g.set(title=f"Simulated {self.operation} {column_name} CDF ({self.label})",
              xlabel=f"Simulated {column_opts['xlabel_tag']}", ylabel=f"{self.operation} {column_opts['ylabel_tag']}")
        fig = g.get_figure()
        fig.savefig(self.targetFolder+f"/{self.operation.lower()}_{column_name}_cdf.png")
        plt.show()

    def plot_pdf(self,  column_name, column_opts):
        df = self.df.sort_values(column_name)
        # Histogram
        bins = 8
        sns.set()
        g = sns.histplot(x=df[column_name], bins=bins)
        g.set(title=f"Simulated lookup {column_name} PDF ({self.label})",
              xlabel=f"Simulated {column_opts['xlabel_tag']}", ylabel=f"Lookups {column_opts['ylabel_tag']}")
        fig = g.get_figure()
        fig.savefig(self.targetFolder + f"/lookup_{column_name}_pdf.png")
        plt.show()


# --- Multiple Aggregators ---
class CombinedMetrics:
    metrics = {
        "lookup_aggregated_delay": {
            "title_tag": "delay",
            "xlabel_tag": "delay (ms)",
            "ylabel_tag": "",
        },
        "finished_connection_attempts": {
            "title_tag": "hops",
            "xlabel_tag": "hops",
            "ylabel_tag": "",
        },
        "accuracy": {
            "title_tag": "accuracy",
            "xlabel_tag": "accuracy",
            "ylabel_tag": "",
        },
    }

    def __init__(self, files, aggregator, filters, operation, output_image_folder, metrics, legend):
        self.files = files
        self.dfs = []
        self.tags = []
        self.params = []
        self.tag = aggregator
        self.filters = filters
        self.operation = operation
        # add metrics to pre-existing ones
        self.metrics.update(metrics)
        for file in files:
            if any(filter not in file for filter in filters):
                continue

            self.dfs.append(pd.read_csv(file))
            raw_tag = file.split("/")[-1].replace(".csv", "")
            params = tag_parser(raw_tag)
            tag = compose_legend(params, legend)
            self.params.append(params)
            self.tags.append(tag)

        self.udf = self.unify_dfs(self.dfs)  # unified dataframe

        self.targetFolder = output_image_folder+f"/{self.operation.lower}_comparison_{aggregator}"
        make_folder(self.targetFolder, f"for keeping the {self.operation} related images about {self.tag}\n")
        print(f"plotting by {aggregator}, saving figures at {self.targetFolder}\n")

        # --- plotting sequence ---
        for metrics_name, metrics_opts in self.metrics.items():
            self.plot_cdfs_by(aggregator, metrics_name, metrics_opts)
            self.plot_pdfs_by(aggregator, metrics_name, metrics_opts)

    def unify_dfs(self, dfs):
        return pd.concat(dfs)

    def plot_cdfs_by(self, aggregator_tag, column_name, column_opts):
        # CDF
        sns.set()
        palette = sns.color_palette(n_colors=len(self.dfs))
        for i, df in enumerate(self.dfs):
            df = df.sort_values(column_name)
            g = sns.lineplot(data=df, x=column_name, y=np.linspace(0, 1, len(df)), label=self.tags[i],
                             ci=None, color=palette[i])
            g.set(title=f"Simulated {self.operation} {column_opts['title_tag']} CDF (by {aggregator_tag})",
                  xlabel=f"Simulated {column_opts['xlabel_tag']}",
                  ylabel=f"{self.operation} {column_opts['ylabel_tag']} CDF")
        plt.legend(loc='lower center', ncols=1,  bbox_to_anchor=(0.5, -0.2+(-0.065*len(self.dfs))))
        fig = g.get_figure()
        fig.savefig(self.targetFolder+f"/simulated_{self.operation.lower()}_{column_name}_cdf.png")
        plt.show()

    def plot_pdfs_by(self, aggregator_tag, column_name, column_opts):
        # Histogram
        sns.set()
        by_aggregator = self.udf.groupby([column_name, aggregator_tag]).count()
        df = by_aggregator.reset_index()
        g = sns.histplot(data=df, x=df[column_name])
        """
        g = sns.barplot(data=df, x=df[column_name], y="Unnamed: 0", hue=aggregator_tag, width=1.2)
        """
        g.set(title=f"Simulated {self.operation} {column_opts['title_tag']} PDF (by {aggregator_tag})",
              xlabel=f"Simulated {column_opts['xlabel_tag']}",
              ylabel=f"{self.operation} {column_opts['ylabel_tag']}")
        plt.legend(loc='lower center', ncols=1,  bbox_to_anchor=(0.5, -0.2+(-0.065*len(self.dfs))))
        fig = g.get_figure()
        fig.savefig(self.targetFolder+f"/simulated_{self.operation.lower()}_{column_name}_hist.png")
        plt.show()
