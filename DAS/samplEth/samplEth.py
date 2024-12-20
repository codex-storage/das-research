import hashlib
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import random
import os
import sys
from datetime import datetime
import networkx as nx
import csv
import numpy as np
import time
import math
import json
import concurrent.futures

# # debug file
# class DualOutput:
#     def __init__(self, file_path):
#         self.terminal = sys.stdout
#         self.log = open(file_path, "w")

#     def write(self, message):
#         self.terminal.write(message)
#         self.log.write(message)

#     def flush(self):
#         self.terminal.flush()
#         self.log.flush()



# results_dir = "results"
# debug_file_path = os.path.join(results_dir, "debug.log")
# os.makedirs(results_dir, exist_ok=True)
# sys.stdout = DualOutput(debug_file_path)


RANDOM_SEED = 30052001
random.seed(RANDOM_SEED)


num_rows = 512
num_cols = 512
connections_per_peer = [[50, 100], [100, 150], [150, 200]]

min_custody = 2
val_custody = 2
flat_custody = False

# poison nodes by value
row_number = 3  # 1 -> Country (United States), 2 -> Company (Amazon, Oracle), 3 -> ISP (lighthouse, teku, prysm)
row_value = 'prysm'

# poison nodes by %
poison_by_percentage = True
poison_percentage = 90

# query methods
exponential_growth = False
linear_growth = True
linear_constant_growth = False
hybrid_growth = False
exponential_constant_growth = False
linear_growth_constant = 10



def plot_peer_coverage(selected_node, peer_connections, peer_custody, peer_poison_map, results_folder):
    
    rows_count = [0] * 512
    cols_count = [0] * 512
    rows_count_without_poisonous_nodes = [0] * 512
    cols_count_without_poisonous_nodes = [0] * 512
    
    if selected_node in peer_connections:
        for peer in peer_connections[selected_node]:
            if peer in peer_custody:
                for row in peer_custody[peer]['rows']:
                    rows_count[row] += 1
                    if peer_poison_map[peer] == 0:
                        rows_count_without_poisonous_nodes[row] += 1
                for col in peer_custody[peer]['cols']:
                    cols_count[col] += 1
                    if peer_poison_map[peer] == 0:
                        cols_count_without_poisonous_nodes[col] += 1

    # First figure with all peers
    plt.figure(figsize=(14, 7))
    plt.subplots_adjust(top=0.8)
    plt.figtext(
        0.2, 0.96,  # Adjusted x-coordinate to shift left
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )

    # Plot for rows
    plt.subplot(1, 2, 1)
    plt.bar(range(512), rows_count, color='blue')
    plt.xlabel('Row Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Peer Coverage - Rows', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)

    # Plot for columns
    plt.subplot(1, 2, 2)
    plt.bar(range(512), cols_count, color='green')
    plt.xlabel('Column Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Peer Coverage - Columns', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)

    os.makedirs(results_folder, exist_ok=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to prevent overlap with the top text box
    plt.savefig(os.path.join(results_folder, 'peer_coverage.png'), bbox_inches='tight')
    plt.close()

    # Second figure with only honest peers
    plt.figure(figsize=(14, 7))
    plt.subplots_adjust(top=0.8)
    plt.figtext(
        0.2, 0.96,  # Adjusted x-coordinate to shift left
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round') 
    )

    plt.subplot(1, 2, 1)
    plt.bar(range(512), rows_count_without_poisonous_nodes, color='orange')
    plt.xlabel('Row Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Peer Coverage - Rows (Honest Peers)', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.subplot(1, 2, 2)
    plt.bar(range(512), cols_count_without_poisonous_nodes, color='purple')
    plt.xlabel('Column Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Peer Coverage - Columns (Honest Peers)', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(os.path.join(results_folder, 'peer_coverage_honest.png'), bbox_inches='tight')
    plt.close()




def calculate_peer_coverage_cells(selected_node, peer_connections, peer_custody, peer_poison_map):
    
    # Initialize count for cells
    cell_count = [0] * (num_rows * num_cols)
    cell_count_without_poisonous_nodes = [0] * (num_rows * num_cols)
    
    # Check if the selected node has connections
    if selected_node in peer_connections:
        for peer in peer_connections[selected_node]:
            if peer in peer_custody:
                # Count all cells in the covered rows
                for row in peer_custody[peer]['rows']:
                    for col in range(num_cols):  # Count all columns for the row
                        cell_index = row * num_cols + col
                        cell_count[cell_index] += 1
                        if peer_poison_map.get(peer, 0) == 0:
                            cell_count_without_poisonous_nodes[cell_index] += 1

                # Count all cells in the covered columns
                for col in peer_custody[peer]['cols']:
                    for row in range(num_rows):  # Count all rows for the column
                        cell_index = row * num_cols + col
                        cell_count[cell_index] += 1
                        if peer_poison_map.get(peer, 0) == 0:
                            cell_count_without_poisonous_nodes[cell_index] += 1

                # for row in peer_custody[peer]['rows']:
                #     for col in peer_custody[peer]['cols']:
                #         cell_index = row * num_cols + col
                #         cell_count[cell_index] -= 1
                #         if peer_poison_map.get(peer, 0) == 0:
                #             cell_count_without_poisonous_nodes[cell_index] -= 1
                        
    return cell_count, cell_count_without_poisonous_nodes



def plot_peer_coverage_cells(cell_count, results_folder):

    # Create a box plot for cells with increased width to make space for the textbox
    plt.figure(figsize=(14, 7))
    plt.subplots_adjust(top=0.9)
    plt.boxplot(cell_count, patch_artist=True, boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'), medianprops=dict(color='red'))
    plt.xlabel('Cells', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Peer Coverage - Cells', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    os.makedirs(results_folder, exist_ok=True)
    plt.savefig(os.path.join(results_folder, 'peer_coverage_cells_boxplot.png'))
    plt.close()



def plot_peer_coverage_cells_without_poisonous_nodes(cell_count_without_poisonous_nodes, output_dir):

    plt.figure(figsize=(14, 7))
    plt.subplots_adjust(top=0.9)
    plt.boxplot(cell_count_without_poisonous_nodes, patch_artist=True, boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'), medianprops=dict(color='red'))
    plt.xlabel('Cells', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.title('Level 1 Honest Peer Coverage - Cells', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'peer_coverage_cells_without_poisonous_nodes_boxplot.png'))
    plt.close()



def plot_peer_coverage_cells_all(peerIDs, peer_connections, peer_custody, results_folder):

    cell_count_sum = np.zeros(num_rows * num_cols, dtype=np.uint32)
    cell_count_min = np.full(num_rows * num_cols, np.inf, dtype=np.float32)
    cell_count_max = np.zeros(num_rows * num_cols, dtype=np.uint32)
    
    for i, selected_node in enumerate(peerIDs):
        cell_count = np.zeros(num_rows * num_cols, dtype=np.uint32)
        
        if selected_node in peer_connections:
            for peer in peer_connections[selected_node]:
                if peer in peer_custody:
                    # Count all cells in the covered rows
                    for row in peer_custody[peer]['rows']:
                        for col in range(num_cols):
                            cell_index = row * num_cols + col
                            cell_count[cell_index] += 1

                    for col in peer_custody[peer]['cols']:
                        for row in range(num_rows):
                            cell_index = row * num_cols + col
                            cell_count[cell_index] += 1
        
        cell_count_sum += cell_count
        cell_count_min = np.minimum(cell_count_min, cell_count)
        cell_count_max = np.maximum(cell_count_max, cell_count)

        if i==800: break

    cell_count_avg = cell_count_sum / 801

    plt.figure(figsize=(20, 8))
    plt.plot(range(num_rows * num_cols), cell_count_min, color='blue', label='Min Peer Coverage', linestyle='-', linewidth=0.2)
    plt.plot(range(num_rows * num_cols), cell_count_avg, color='green', label='Avg Peer Coverage', linestyle='-', linewidth=0.2)
    plt.plot(range(num_rows * num_cols), cell_count_max, color='red', label='Max Peer Coverage', linestyle='-', linewidth=0.2)
    plt.xlabel('Cell Index', fontsize=16)
    plt.ylabel('Peer Coverage',fontsize=16)
    plt.title('Peer Coverage - Cells (Min, Avg, Max)', fontsize=16)
    plt.legend(loc='upper right')
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    os.makedirs(results_folder, exist_ok=True)
    plt.savefig(os.path.join(results_folder, 'peer_coverage_combined.png'))
    plt.close()

    with open(os.path.join(results_folder, 'peer_coverage_stats.txt'), 'w') as f:
        f.write('cell_count_min = [')
        f.write(', '.join(map(str, cell_count_min)))
        f.write(']\n\n')

        f.write('cell_count_avg = [')
        f.write(', '.join(map(str, cell_count_avg)))
        f.write(']\n\n')

        f.write('cell_count_max = [')
        f.write(', '.join(map(str, cell_count_max)))
        f.write(']\n')



def calculate_cells_formula(vpn):
    result = (min_custody + vpn * val_custody) * (num_rows/2 + num_cols/2)
    return (min(result, 256*516) * 256) / (1024*1024)

def plot_node_cells_downloaded(node_data, results_folder):

    node_numbers = list(node_data.keys())
    second_column_values = [data[1] for data in node_data.values()]
    formula_results = [
        calculate_cells_formula(second_column_values[i])
        for i in range(len(node_numbers))
    ]
    plt.figure(figsize=(14, 5))
    plt.boxplot(formula_results, vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='darkgreen'))
    plt.title('Amount of Data Downloaded by Nodes', fontsize=16)
    plt.xlabel('Megabytes', fontsize=16)
    plt.tight_layout()
    plt.grid(True, axis='x', which='both', color='gray', linestyle='--', linewidth=0.5)
    max_value = max(formula_results)
    x_ticks = np.arange(0, max_value + 2, 2)
    plt.xticks(x_ticks)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(results_folder, exist_ok=True)
    plt.savefig(os.path.join(results_folder, 'node_data_custom_formula_boxplot.png'))
    plt.close()




def print_horizon_cells_statistics(horizon_data_cells, connections_values):
    print("Calculating and printing horizon by cells statistics for each connections_per_peer value...\n")

    for i, cells in enumerate(horizon_data_cells):
        print(f"Statistics for {connections_values[i]} connections per peer:")
        mean_value = np.mean(cells)
        quartiles = np.percentile(cells, [25, 50, 75])
        print(f"Mean: {mean_value:.2f}")
        print(f"1st Quartile: {quartiles[0]:.2f}")
        print(f"Median (2nd Quartile): {quartiles[1]:.2f}")
        print(f"3rd Quartile: {quartiles[2]:.2f}")
        print("-" * 40)
    print("Finished printing horizon by cells statistics.\n")



def plot_node_data(node_data, results_folder):
    node_numbers = list(node_data.keys())
    second_column_values = [data[1] for data in node_data.values()]
    sorted_second_column_values = sorted(second_column_values)

    plt.figure(figsize=(14, 7))

    # Bar plot
    plt.subplot(1, 2, 1)
    plt.bar(node_numbers, sorted_second_column_values, color='blue')
    plt.title('Node-validators distribution', fontsize=16)
    plt.xlabel('Node Number', fontsize=16)
    plt.ylabel('Number of Validators', fontsize=16)
    plt.yscale('log')
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    # Box plot
    plt.subplot(1, 2, 2)
    plt.boxplot(second_column_values, vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'))
    plt.title('Node-validators distribution', fontsize=16)
    plt.xlabel('Number of Validators', fontsize=16)
    plt.xscale('log')
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(results_folder, exist_ok=True)
    plt.savefig(os.path.join(results_folder, 'node_data_plots.png'))
    plt.close()


def hash_peer(peerID, iteration):
    modified_peerID = peerID + str(iteration)
    sha256 = hashlib.sha256(modified_peerID.encode('utf-8')).hexdigest()
    binary_hash = bin(int(sha256, 16))[2:].zfill(256)
    segment = binary_hash[-10:]
    return segment



def assign_rows_cols(peerIDs, node_data):
    print("Starting to assign rows and columns to peers...")
    
    peer_custody = defaultdict(lambda: {'rows': set(), 'cols': set()})
    row_custody = defaultdict(set)
    col_custody = defaultdict(set)
    
    for i, peerID in enumerate(peerIDs):
        if flat_custody:
            total_custody = min_custody
        else:
            total_custody = min_custody + node_data[i][1] * val_custody
            total_custody = min(total_custody, num_rows)

        iteration = 0
        while len(peer_custody[peerID]['rows']) < total_custody or len(peer_custody[peerID]['cols']) < total_custody:
            binary_hash = hash_peer(peerID, iteration)
            bit_type = int(binary_hash[-1])
            index = int(binary_hash[:-1], 2)
            
            if bit_type == 0 and len(peer_custody[peerID]['rows']) < total_custody:
                if index < num_rows and index not in peer_custody[peerID]['rows']:
                    peer_custody[peerID]['rows'].add(index)
                    row_custody[index].add(peerID)
                    
            elif bit_type == 1 and len(peer_custody[peerID]['cols']) < total_custody:
                if index < num_cols and index not in peer_custody[peerID]['cols']:
                    peer_custody[peerID]['cols'].add(index)
                    col_custody[index].add(peerID)
                    
            iteration += 1
                
        print(f"Peer index {i} custody assignment: rows - {sorted(peer_custody[peerID]['rows'])}, cols - {sorted(peer_custody[peerID]['cols'])}")
    
    print("Finished assigning rows and columns to peers.")
    return peer_custody, row_custody, col_custody




def plot_custody_distribution(row_custody, col_custody, peer_poison_map, results_folder):
    
    row_counts = [len(peers) for peers in row_custody.values()]
    col_counts = [len(peers) for peers in col_custody.values()]
    
    def filter_non_poisonous(peers):
        return [peer for peer in peers if peer_poison_map.get(peer, 0) == 0]

    row_counts_without_poisonous = [len(filter_non_poisonous(peers)) for peers in row_custody.values()]
    col_counts_without_poisonous = [len(filter_non_poisonous(peers)) for peers in col_custody.values()]

    plt.figure(figsize=(14, 7))
    
    plt.subplot(1, 2, 1)
    plt.bar(range(len(row_counts)), row_counts, color='blue')
    plt.title('Row Custody Distribution', fontsize=16)
    plt.xlabel('Row Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    
    plt.subplot(1, 2, 2)
    plt.bar(range(len(col_counts)), col_counts, color='green')
    plt.title('Column Custody Distribution', fontsize=16)
    plt.xlabel('Column Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'custody_distribution.png'))
    plt.close()


    # Plot custody distribution without poisonous peers
    plt.figure(figsize=(14, 7))
    plt.subplot(1, 2, 1)
    plt.bar(range(len(row_counts_without_poisonous)), row_counts_without_poisonous, color='blue')
    plt.title('Row Custody Distribution (Honest Peers)', fontsize=16)
    plt.xlabel('Row Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.subplot(1, 2, 2)
    plt.bar(range(len(col_counts_without_poisonous)), col_counts_without_poisonous, color='green')
    plt.title('Column Custody Distribution (Honest Peers)', fontsize=16)
    plt.xlabel('Column Index', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'custody_distribution_non_poisonous.png'))
    plt.close()
    


def plot_custody_distribution_boxplot(row_custody, col_custody, peer_poison_map, results_folder):

    row_counts = [len(peers) for peers in row_custody.values()]
    col_counts = [len(peers) for peers in col_custody.values()]

    def filter_non_poisonous(peers):
        return [peer for peer in peers if peer_poison_map.get(peer, 0) == 0]

    row_counts_without_poisonous = [len(filter_non_poisonous(peers)) for peers in row_custody.values()]
    col_counts_without_poisonous = [len(filter_non_poisonous(peers)) for peers in col_custody.values()]

    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.boxplot(row_counts, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'))
    plt.title('Row Custody Distribution', fontsize=16)
    plt.xlabel('Number of Peers', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.subplot(1, 2, 2)
    plt.boxplot(col_counts, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='red'))
    plt.title('Column Custody Distribution', fontsize=16)
    plt.xlabel('Number of Peers', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'custody_distribution_boxplots.png'))
    plt.close()


    # Plot boxplot for non-poisonous peers only
    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.boxplot(row_counts_without_poisonous, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'))
    plt.title('Row Custody Distribution (Honest Peers)', fontsize=16)
    plt.xlabel('Number of Peers', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.subplot(1, 2, 2)
    plt.boxplot(col_counts_without_poisonous, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='red'))
    plt.title('Column Custody Distribution (Honest Peers)', fontsize=16)
    plt.xlabel('Number of Peers', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'custody_distribution_boxplots_non_poisonous.png'))
    plt.close()



# for every connection
def plot_horizon_distribution(peer_horizon, results_folder):

    peer_ids = list(peer_horizon.keys())
    num_peers = len(peer_ids)
    
    unique_rows_seen = [0] * num_peers
    unique_cols_seen = [0] * num_peers

    for i, peer in enumerate(peer_ids):
        unique_rows_seen[i] = len(peer_horizon[peer]['rows'])
        unique_cols_seen[i] = len(peer_horizon[peer]['cols'])

    for i in range(num_peers):
        if unique_rows_seen[i] >= num_rows / 2:
            unique_rows_seen[i] = num_rows

        if unique_cols_seen[i] >= num_cols / 2:
            unique_cols_seen[i] = num_cols
    
    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.bar(range(num_peers), unique_rows_seen, color='blue')
    plt.title('Horizon level 1 Rows', fontsize=16)
    plt.xlabel('Peer Index', fontsize=16)
    plt.ylabel('Number of Rows', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    
    plt.subplot(1, 2, 2)
    plt.bar(range(num_peers), unique_cols_seen, color='green')
    plt.title('Horizon level 1 Columns', fontsize=16)
    plt.xlabel('Peer Index')
    plt.ylabel('Number of Columns', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_distribution.png'))
    plt.close()

    # Plot boxplots for horizon level 1 rows and columns
    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.boxplot(unique_rows_seen, patch_artist=True, boxprops=dict(facecolor='blue', color='blue'), vert=False)
    plt.title('Horizon level 1 Rows', fontsize=16)
    plt.xlabel('Number of Rows Seen by Each Peer', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)
    
    plt.subplot(1, 2, 2)
    plt.boxplot(unique_cols_seen, patch_artist=True, boxprops=dict(facecolor='green', color='green'), vert=False)
    plt.title('Horizon level 1 Columns', fontsize=16)
    plt.xlabel('Number of Columns Seen by Each Peer', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)

    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_boxplot.png'))




# for every connection
def plot_horizon_distribution_boxplot(peer_horizon, results_folder):

    peer_ids = list(peer_horizon.keys())
    num_peers = len(peer_ids)
    
    unique_rows_seen = [len(peer_horizon[peer]['rows']) for peer in peer_ids]
    unique_cols_seen = [len(peer_horizon[peer]['cols']) for peer in peer_ids]

    for i in range(num_peers):
        if unique_rows_seen[i] >= num_rows / 2:
            unique_rows_seen[i] = num_rows
        
        if unique_cols_seen[i] >= num_cols / 2:
            unique_cols_seen[i] = num_cols

    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.boxplot(unique_rows_seen, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'))
    plt.title('Horizon level 1 Rows', fontsize=16)
    plt.xlabel('Horizon level 1 Rows', fontsize=16)
    
    plt.subplot(1, 2, 2)
    plt.boxplot(unique_cols_seen, vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='red'))
    plt.title('Horizon level 1 Columns', fontsize=16)
    plt.xlabel('Horizon level 1 Columns', fontsize=16)

    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_distribution_boxplot.png'))




def load_node_data(csv_file):
    peerIDs = []
    node_data = {}
    todes_data = {}

    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            peerID = row[0]
            peerIDs.append(peerID)
            node_name = int(row[1].replace("node", ""))

            # Extract node_data 
            node_values = list(map(int, row[2:6]))
            node_data[node_name] = node_values

            # Extract todes_data
            todes_values = row[7:11] 
            todes_data[node_name] = todes_values

    return peerIDs, node_data, todes_data



def map_peerIDs_to_values(peerIDs, node_data):
    peerID_to_val = {}
    for key, peerID in enumerate(peerIDs):
        if key in node_data:
            peerID_to_val[peerID] = node_data[key][1]
        else:
            peerID_to_val[peerID] = None

    return peerID_to_val


def mark_poisoned_nodes(peerIDs, node_data, todes_data):
    peer_poison_map = {}

    for i, node_id in enumerate(node_data):
        i = i % len(peerIDs)
        peer_id = peerIDs[i]
        
        if todes_data[node_id][row_number] == row_value:
            peer_poison_map[peer_id] = 1 
        else:
            peer_poison_map[peer_id] = 0
    
    print("Peer Poison Map")
    # Get indexes of poisonous and non-poisonous peers
    poisonous_indexes = sorted([i for i, peer_id in enumerate(peerIDs) if peer_poison_map.get(peer_id) == 1])
    non_poisonous_indexes = sorted([i for i, peer_id in enumerate(peerIDs) if peer_poison_map.get(peer_id) == 0])

    print("Poisonous Peer Indexes (sorted):", poisonous_indexes)
    print("Non-Poisonous Peer Indexes (sorted):", non_poisonous_indexes)

    return peer_poison_map



def mark_poisoned_nodes_by_percentage(peerIDs):
    peer_poison_map = {peer_id: 0 for peer_id in peerIDs}

    num_peers_to_poison = int(len(peerIDs) * poison_percentage / 100)
    poisoned_peers = random.sample(peerIDs, num_peers_to_poison)
    for peer_id in poisoned_peers:
        peer_poison_map[peer_id] = 1

    print("Peer Poison Map")
    # Get indexes of poisonous and non-poisonous peers
    poisonous_indexes = sorted([i for i, peer_id in enumerate(peerIDs) if peer_poison_map.get(peer_id) == 1])
    non_poisonous_indexes = sorted([i for i, peer_id in enumerate(peerIDs) if peer_poison_map.get(peer_id) == 0])

    print("Poisonous Peer Indexes (sorted):", poisonous_indexes)
    print("Non-Poisonous Peer Indexes (sorted):", non_poisonous_indexes)

    return peer_poison_map




def connect_peers(peerIDs, connections_range):
    print("Starting peer connection process...")
    peer_connections = defaultdict(set)
    reached_target = []
    
    for peer in peerIDs:
        num_connections = random.randint(connections_range[0], connections_range[1])
        available_peers = peerIDs[:]
        random.shuffle(available_peers)
        
        while len(peer_connections[peer]) < num_connections and available_peers:
            other_peer = available_peers.pop()
            if other_peer != peer and len(peer_connections[other_peer]) < num_connections:
                peer_connections[peer].add(other_peer)
                peer_connections[other_peer].add(peer)

        peer_index = peerIDs.index(peer)
        reached_target.append(peer_index)

    print("\nPeers that reached the target connections:")
    for peer_index in sorted(reached_target):
        connected_indices = sorted(peerIDs.index(p) for p in peer_connections[peerIDs[peer_index]])
        print(f"Peer index {peer_index} connected to peers {connected_indices}")
    
    print("\nPeer connection process completed.")
    return peer_connections




def calculate_horizon_level_2(peer_custody, peer_connections, peer_poison_map):

    peer_horizon_level_2 = {}

    for peer in peer_custody:
        if peer_poison_map.get(peer, 0) == 1:
            continue

        level_2_rows = set(peer_custody[peer]['rows'])
        level_2_cols = set(peer_custody[peer]['cols'])
        
        neighbors = peer_connections.get(peer, [])
        
        for neighbor in neighbors:
            if peer_poison_map.get(neighbor, 0) == 1:
                continue

            # If we've already reached the maximum possible rows/columns, stop further additions
            if len(level_2_rows) < num_rows:
                level_2_rows.update(peer_custody[neighbor]['rows'])
            if len(level_2_cols) < num_cols:
                level_2_cols.update(peer_custody[neighbor]['cols'])

            # Get neighbors of neighbors (second hop)
            second_hop_neighbors = peer_connections.get(neighbor, [])
            
            # Add second hop neighbors' custody to the level 2 horizon
            for second_hop_neighbor in second_hop_neighbors:
                if peer_poison_map.get(second_hop_neighbor, 0) == 1:
                    continue

                if len(level_2_rows) < num_rows:
                    level_2_rows.update(peer_custody[second_hop_neighbor]['rows'])
                if len(level_2_cols) < num_cols:
                    level_2_cols.update(peer_custody[second_hop_neighbor]['cols'])

                if len(level_2_rows) >= num_rows and len(level_2_cols) >= num_cols:
                    break
            if len(level_2_rows) >= num_rows and len(level_2_cols) >= num_cols:
                break

        peer_horizon_level_2[peer] = {
            'rows': level_2_rows,
            'cols': level_2_cols
        }

    return peer_horizon_level_2





def calculate_horizon_cells_level_2(peer_horizon_level_2):
    print("Calculating level 2 horizon by cells for each peer...")

    horizon_cells_level_2 = []
    total_cells = num_rows * num_cols

    for peer in peer_horizon_level_2:
        rows_seen = len(peer_horizon_level_2[peer]['rows'])
        cols_seen = len(peer_horizon_level_2[peer]['cols'])
        if rows_seen >= num_rows / 2 or cols_seen >= num_cols / 2:
            cells_seen = num_rows * num_cols
        else: 
            cells_seen = rows_seen * num_cols + cols_seen * num_rows - rows_seen * cols_seen
        normalized_cells_seen = (cells_seen * 100.0) / total_cells  # Ensure float division
        horizon_cells_level_2.append(normalized_cells_seen)

    return horizon_cells_level_2




def calculate_horizon(peer_custody, peer_connections, peer_poison_map):
    print("Starting horizon calculation...")
    peer_horizon = defaultdict(lambda: {'rows': set(), 'cols': set()})
    
    for peer, connections in peer_connections.items():
        # Skip poisoned peers
        if peer_poison_map.get(peer, 0) == 1:
            continue

        horizon_rows = set(peer_custody[peer]['rows'])
        horizon_cols = set(peer_custody[peer]['cols'])
        
        for connected_peer in connections:
            # Skip poisoned connected peers
            if peer_poison_map.get(connected_peer, 0) == 1:
                continue
            
            horizon_rows.update(peer_custody[connected_peer]['rows'])
            horizon_cols.update(peer_custody[connected_peer]['cols'])
            
        # Update the peer horizon with the final calculated rows and cols
        peer_horizon[peer]['rows'] = horizon_rows
        peer_horizon[peer]['cols'] = horizon_cols
        
    return peer_horizon



def calculate_horizon_cells(peer_horizon):

    horizon_cells = []
    horizon_cells_count = []
    total_cells = num_rows * num_cols

    for peer in peer_horizon:
        rows_seen = len(peer_horizon[peer]['rows'])
        cols_seen = len(peer_horizon[peer]['cols'])
        if rows_seen >= num_rows / 2 or cols_seen >= num_cols / 2:
            cells_seen = num_rows * num_cols
        else:
            cells_seen = rows_seen * num_cols + cols_seen * num_rows - rows_seen * cols_seen
        horizon_cells_count.append(cells_seen)
        normalized_cells_seen = (cells_seen * 100.0) / total_cells 
        horizon_cells.append(normalized_cells_seen)

    return horizon_cells




def print_horizon_statistics(horizon_data):
    print("Horizon statistics:")

    for i, horizon in enumerate(horizon_data):
        rows = np.array(horizon['rows'])
        cols = np.array(horizon['cols'])

        # Calculate statistics for rows
        rows_mean = np.mean(rows)
        rows_q1 = np.percentile(rows, 25)
        rows_median = np.median(rows)
        rows_q3 = np.percentile(rows, 75)

        # Calculate statistics for columns
        cols_mean = np.mean(cols)
        cols_q1 = np.percentile(cols, 25)
        cols_median = np.median(cols)
        cols_q3 = np.percentile(cols, 75)

        print(f"\nGroup {i+1} Statistics:")
        print("Rows:")
        print(f"Mean: {rows_mean:.2f}, 1st Quartile (Q1): {rows_q1:.2f}, Median (Q2): {rows_median:.2f}, 3rd Quartile (Q3): {rows_q3:.2f}")
        print("Columns:")
        print(f"Mean: {cols_mean:.2f}, 1st Quartile (Q1): {cols_q1:.2f}, Median (Q2): {cols_median:.2f}, 3rd Quartile (Q3): {cols_q3:.2f}")

    print("Finished printing horizon statistics.")



def plot_horizon_distribution_boxplot(horizon_data, results_folder):

    plt.figure(figsize=(16, 7))

    num_groups = len(horizon_data)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1,num_groups+1)]

    # Plot for Rows
    plt.subplot(1, 2, 1)
    plt.boxplot([horizon['rows'] for horizon in horizon_data], vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'),
                labels=labels)
    plt.title('Number of rows nodes can see at horizon level 1', fontsize=16)
    plt.xlabel('Number of rows', fontsize=16)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.tight_layout()

    # Plot for Columns
    plt.subplot(1, 2, 2)
    plt.boxplot([horizon['cols'] for horizon in horizon_data], vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='red'),
                labels=labels)
    plt.title('Number of columns nodes can see at horizon level 1', fontsize=16)
    plt.xlabel('Number of columns', fontsize=16)

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.4, top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_distribution_boxplot_comparison.png'))





def plot_horizon_cells_distribution_boxplot(horizon_data, results_folder):
    
    plt.figure(figsize=(14, 7))
    num_groups = len(horizon_data)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1,num_groups+1)]
    box = plt.boxplot(horizon_data, vert=False, patch_artist=True,
                      boxprops=dict(facecolor='lightcoral', color='red'),
                      whiskerprops=dict(color='red'),
                      medianprops=dict(color='darkred'),
                      labels=labels)
    plt.xlim(0, 105)
    plt.title('Percentage of cells nodes can see at horizon level 1', fontsize=16)
    plt.xlabel('%', fontsize=16)
    plt.ylabel('Connection Ranges', fontsize=16)
    plt.tight_layout()
    plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_cells_distribution_boxplot_comparison.png'))
    plt.close()





def print_horizon_statistics_level_2(peer_horizon_level_2):
    print("Calculating and printing level 2 horizon statistics...")

    horizon_rows_level_2 = [
        len(horizon['rows']) if len(horizon['rows']) < num_rows / 2 else num_rows
        for horizon in peer_horizon_level_2.values()
    ]

    horizon_cols_level_2 = [
        len(horizon['cols']) if len(horizon['cols']) < num_cols / 2 else num_cols
        for horizon in peer_horizon_level_2.values()
    ]

    # Calculate statistics
    row_mean_level_2 = np.mean(horizon_rows_level_2)
    col_mean_level_2 = np.mean(horizon_cols_level_2)

    row_quartiles_level_2 = np.percentile(horizon_rows_level_2, [25, 50, 75])
    col_quartiles_level_2 = np.percentile(horizon_cols_level_2, [25, 50, 75])

    # Print statistics
    print(f"Horizon level 2 Rows Statistics:")
    print(f"Mean: {row_mean_level_2:.2f}")
    print(f"1st Quartile: {row_quartiles_level_2[0]:.2f}")
    print(f"Median (2nd Quartile): {row_quartiles_level_2[1]:.2f}")
    print(f"3rd Quartile: {row_quartiles_level_2[2]:.2f}")

    print(f"Horizon level 2 Columns Statistics:")
    print(f"Mean: {col_mean_level_2:.2f}")
    print(f"1st Quartile: {col_quartiles_level_2[0]:.2f}")
    print(f"Median (2nd Quartile): {col_quartiles_level_2[1]:.2f}")
    print(f"3rd Quartile: {col_quartiles_level_2[2]:.2f}")

    print("Finished printing level 2 horizon statistics.")



def plot_horizon_distribution_boxplot_level_2(horizon_data_level_2, results_folder):
    plt.figure(figsize=(16, 7))
    num_groups = len(horizon_data_level_2)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1,num_groups+1)]

    # Plot for Rows
    plt.subplot(1, 2, 1)
    plt.boxplot([horizon['rows'] for horizon in horizon_data_level_2], vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'),
                labels=labels)
    plt.title('Horizon level 2 Rows', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.xlabel('Number of Rows', fontsize=16)

    # Plot for Columns
    plt.subplot(1, 2, 2)
    plt.boxplot([horizon['cols'] for horizon in horizon_data_level_2], vert=False, patch_artist=True, 
                boxprops=dict(facecolor='lightgreen', color='green'),
                whiskerprops=dict(color='green'),
                medianprops=dict(color='red'),
                labels=labels)
    plt.title('Horizon level 2 Columns', fontsize=16)
    plt.xlabel('Number Columns', fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.4, top=0.9)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_distribution_boxplot_comparison_level_2.png'))





def plot_horizon_cells_distribution_boxplot_level_2(horizon_data_level_2, results_folder):
    plt.figure(figsize=(14, 7))

    num_groups = len(horizon_data_level_2)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1,num_groups+1)]
    plt.boxplot(horizon_data_level_2, vert=False, patch_artist=True,
                boxprops=dict(facecolor='lightcoral', color='red'),
                whiskerprops=dict(color='red'),
                medianprops=dict(color='darkred'),
                labels=labels)
    plt.xlim(0, 110)
    plt.title('Horizon by Cells (%) - Level 2', fontsize=16)
    plt.xlabel('%', fontsize=16)
    plt.ylabel('Connection Ranges', fontsize=16)
    plt.tight_layout()
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'horizon_cells_distribution_boxplot_comparison_level_2.png'))
    plt.close()




def calculate_supernode_distribution(peer_connections, peerID_to_val):
    def count_supernodes(peers):
        x = (num_rows/4 - min_custody)/val_custody
        return sum(1 for peer in peers if peerID_to_val.get(peer, 0) >= x)

    level_1_supernodes_count = []
    level_2_supernodes_count = []

    # Get all peers
    all_peers = list(peer_connections.keys())

    for peer in all_peers:
        # Level 1 connections
        level_1_peers = peer_connections.get(peer, set())
        level_1_supernodes = count_supernodes(level_1_peers)

        # Level 2 connections
        level_2_peers = set()
        for connected_peer in level_1_peers:
            level_2_peers.update(peer_connections.get(connected_peer, set()))
        level_2_peers -= level_1_peers  # Exclude Level 1 peers from Level 2 peers
        level_2_supernodes = count_supernodes(level_2_peers)

        level_1_supernodes_count.append(level_1_supernodes)
        level_2_supernodes_count.append(level_2_supernodes)

    return level_1_supernodes_count, level_2_supernodes_count


def plot_supernode_distribution(level_1_supernodes_count, level_2_supernodes_count, connections, results_folder):

    plt.figure(figsize=(14, 6))
    plt.boxplot(level_1_supernodes_count, patch_artist=True,
                boxprops=dict(facecolor='blue', color='blue'),
                medianprops=dict(color='red'))
    plt.title(f'Supernode Distribution - Level 1\nConnection range: {connections[0]} to {connections[1]}', fontsize=16)
    plt.ylabel('Number of Supernodes', fontsize=16)
    plt.yscale('log')
    plt.grid(True, which='both', linestyle='--', linewidth=1)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.minorticks_on()
    plt.grid(True, which='minor', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'supernode_distribution_level_1_boxplot.png'))
    plt.close()

    # Create boxplots for Level 1 and Level 2 supernodes in the same figure
    plt.figure(figsize=(14, 6))
    plt.boxplot([level_1_supernodes_count, level_2_supernodes_count], patch_artist=True,
                boxprops=dict(facecolor='blue', color='blue'),
                medianprops=dict(color='red'),
                labels=['Level 1', 'Level 2'])
    plt.title(f'Supernode Distribution - Level 1 and Level 2 \nConnection range: {connections[0]} to {connections[1]}', fontsize=16)
    plt.ylabel('Number of Supernodes', fontsize=16)
    plt.yscale('log')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.minorticks_on()
    plt.grid(True, which='minor', linestyle=':', linewidth=0.5) 
    plt.tick_params(axis='both', which='major', labelsize=16) 
    plt.tight_layout()
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.subplots_adjust(top=0.85)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'supernode_distribution_boxplot.png'))
    plt.close()



def plot_cell_count_boxplot(cell_count_summary, results_folder):
    plt.figure(figsize=(14, 7))
    num_groups = len(cell_count_summary)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1, num_groups + 1)]
    plt.boxplot(cell_count_summary, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='darkblue'))
    plt.title('Number of peers having each cell across connection ranges', fontsize=16)
    plt.xlabel('Connection Ranges', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(ticks=range(1, num_groups + 1), labels=labels)  # Update x-axis labels
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(results_folder, exist_ok=True)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'cell_count_boxplot.png'))
    plt.close()




def plot_cell_count_without_poisonous_nodes_boxplot(cell_count_summary_without_poisonous_nodes, exec_dir):

    plt.figure(figsize=(14, 7))
    num_groups = len(cell_count_summary_without_poisonous_nodes)
    labels = [f"{i*50} - {(i+1)*50}" for i in range(1, num_groups + 1)]
    plt.boxplot(cell_count_summary_without_poisonous_nodes, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='darkblue'))
    plt.title('Number of honest peers having each cell across connection ranges', fontsize=16)
    plt.xlabel('Connection Ranges', fontsize=16)
    plt.ylabel('Number of Peers', fontsize=16)
    plt.xticks(ticks=range(1, num_groups + 1), labels=labels)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(exec_dir, exist_ok=True)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(exec_dir, 'honest_cell_count_boxplot.png'))
    plt.close()



def plot_peer_coverage_cells_summary(cell_count_summary, connections_per_peer, results_folder):

    data = []
    for cell_count in cell_count_summary:
        data.append(cell_count)

    plt.figure(figsize=(14, 8))
    plt.boxplot(data, patch_artist=True,
                boxprops=dict(facecolor='lightblue', color='blue'),
                whiskerprops=dict(color='blue'),
                medianprops=dict(color='red'),
                labels=[f'{connections} peers' for connections in connections_per_peer])

    plt.xlabel('Connections per Peer Range', fontsize=16)
    plt.ylabel('Cell Peer Coverage', fontsize=16)
    plt.title('Peer Coverage Over Cells - Summary for Different Connection Ranges', fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(results_folder, exist_ok=True)
    plt.subplots_adjust(top=0.85)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(results_folder, 'peer_coverage_cells_summary_boxplot.png'))
    plt.close()



# Cache latency values based on horizon level
latency_cache = {
    "level_1": [random.uniform(0.1, 0.2) for _ in range(1000)],
    "level_2": [random.uniform(0.2, 0.3) for _ in range(1000)],
}

def get_latency(peer_to_query, peer_horizon_level_1, peer_horizon_level_2):
    if peer_to_query in peer_horizon_level_1:
        return random.choice(latency_cache["level_1"])
    elif peer_to_query in peer_horizon_level_2:
        return random.choice(latency_cache["level_2"])
    return None

def generate_random_samples(num_queries):
    return [(random.randint(0, num_rows - 1), random.randint(0, num_cols - 1)) for _ in range(num_queries)]

def query_peer(peer_to_query, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map):
    """Query peer with custody, simulate latency, and return the time taken."""
    if peer_poison_map.get(peer_to_query, 0) == 1:
        return 'timeout', 0.5

    latency = get_latency(peer_to_query, peer_horizon_level_1, peer_horizon_level_2)
    if latency:
        return 'success', latency
    return 'invalid', 0.5


def generate_growth_series():
    if exponential_growth:
        return [2**i for i in range(1000)]
    elif linear_growth:
        linear_part = list(range(10, 201, linear_growth_constant)) 
        return [1] + linear_part
    elif linear_constant_growth:
        series = [1, 10, 20, 30, 40]
        series.extend([40] * 1000)
        return series
    elif hybrid_growth:
        exponential_part = [2**i for i in range(6)]  # [1, 2, 4, 8, 16, 32]
        linear_part = list(range(64, 105, 10))  # [64, 74, 84, 94, 104]
        constant_part = [104] * 1000
        return exponential_part + linear_part + constant_part
    elif exponential_constant_growth:
        exponential_part = [2**i for i in range(6)]  # [1, 2, 4, 8, 16, 32]
        constant_part = [32] * 1000
        return exponential_part + constant_part
    else:
        raise ValueError("No growth method selected!")


def query_peer_with_retries(peers_with_custody, peers_with_custody_level_2, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map, max_retries=10150):
    
    queried_peers = []
    retries = 0
    original_retries = 0

    peers_with_custody = list(set(peers_with_custody))
    peers_with_custody_level_2 = list(set(peers_with_custody_level_2))

    random.shuffle(peers_with_custody)
    random.shuffle(peers_with_custody_level_2)

    growth_series = generate_growth_series()

    for num_peers_to_query in growth_series:
        if retries >= max_retries:
            break
        
        original_retries += num_peers_to_query

        # Query Level 1 peers
        level_1_batch = peers_with_custody[:num_peers_to_query]
        for peer_to_query in level_1_batch:
            queried_peers.append(peer_to_query)
            result, time_taken = query_peer(peer_to_query, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map)

            if result == 'success':
                if retries <= 24:
                    return 'success', time_taken + 0.5 * retries, queried_peers, original_retries
                else:
                    return 'failure', time_taken + 0.5 * retries, queried_peers, original_retries

            elif result == 'timeout':
                if retries >= max_retries:
                    return 'failure', 0.5 * max_retries, queried_peers, original_retries

        # Remove queried Level 1 peers
        peers_with_custody = peers_with_custody[num_peers_to_query:]

        # If all Level 1 peers are queried, move to Level 2 peers
        if not peers_with_custody:
            level_2_batch = peers_with_custody_level_2[:num_peers_to_query]
            for peer_to_query in level_2_batch:
                queried_peers.append(peer_to_query)
                result, time_taken = query_peer(peer_to_query, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map)

                if result == 'success':
                    if retries <= 24:
                        return 'success', time_taken + 0.5 * retries, queried_peers, original_retries
                    else:
                        return 'failure', time_taken + 0.5 * retries, queried_peers, original_retries

                elif result == 'timeout':
                    if retries >= max_retries:
                        return 'failure', 0.5 * max_retries, queried_peers, original_retries

            # Remove queried Level 2 peers
            peers_with_custody_level_2 = peers_with_custody_level_2[num_peers_to_query:]
        
        retries += 1


    return 'failure', 0.5 * retries, queried_peers, original_retries



def query_all_nodes(peerIDs, peer_custody, peer_connections, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map):
    num_queries = 75
    samples = generate_random_samples(num_queries)
    all_query_times = []
    all_results = []
    all_original_retries = []
    all_retries_sum_per_node = []

    max_total_time = 0
    max_peer = None
    max_query_times = []
    queried_peers_for_max_total_time = []
    queried_peers = {} 

    def query_samples_for_peer(peer):
        if peer_poison_map.get(peer, 0) == 1:
            return None

        query_times = []
        results = 'success'
        original_retries_sum = 0
        queried_peers[peer] = []

        for sample_row, sample_col in samples:
            
            if (sample_row in peer_custody.get(peer, {}).get('rows', set()) or
                sample_col in peer_custody.get(peer, {}).get('cols', set())):
                query_times.append(0)
                all_original_retries.extend([0])
            else:
                peers_with_custody = [p for p in peer_connections[peer] if (sample_row in peer_custody.get(p, {}).get('rows', set()) or sample_col in peer_custody.get(p, {}).get('cols', set()))]
                peers_with_custody_level_2 = [p for p in peer_connections if p != peer and p not in peers_with_custody and (sample_row in peer_custody.get(p, {}).get('rows', set()) or sample_col in peer_custody.get(p, {}).get('cols', set()))]

                result, time_taken, queried_peers_list, original_retries = query_peer_with_retries(
                    peers_with_custody, peers_with_custody_level_2, peer_horizon_level_1, peer_horizon_level_2, peer_poison_map
                )
                query_times.append(time_taken)
                if result == 'failure':
                    results = 'failure'
                queried_peers[peer].extend(queried_peers_list)
                original_retries_sum += original_retries
                all_original_retries.extend([original_retries])

        total_time = max(query_times)

        nonlocal max_total_time, max_peer, max_query_times, queried_peers_for_max_total_time
        if total_time > max_total_time:
            max_total_time = total_time
            max_peer = peer
            max_query_times = query_times
            queried_peers_for_max_total_time = queried_peers[peer]

        return total_time, results, original_retries_sum

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(query_samples_for_peer, peer_connections.keys()))

    results = [result for result in results if result is not None]
    all_query_times = [result[0] for result in results]
    all_results = [result[1] for result in results]
    all_retries_sum_per_node = [result[2] for result in results]

    return all_query_times, all_results, all_original_retries, all_retries_sum_per_node



def plot_query_times_boxplot(all_query_times, connections, output_dir):
    """Plot a boxplot for the query times and save it to the results/exec_dir."""
    
    plt.figure(figsize=(14, 7))
    plt.boxplot(all_query_times, patch_artist=True, boxprops=dict(facecolor="lightblue"))
    plt.title(f"Boxplot of Query Times for All Peers\nConnection Range: {connections[0]}-{connections[1]}", fontsize=16)
    plt.ylabel("Query Time (seconds)", fontsize=16)
    plt.xlabel("All Peers", fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    os.makedirs(output_dir, exist_ok=True)
    plt.axhline(y=12, color='red', linestyle='--', linewidth=1)
    plt.subplots_adjust(top=0.85)
    x = ''
    if exponential_growth:
        x = 'Exponential Sampling'
    elif linear_growth:
        x = 'Linear Sampling'
    elif hybrid_growth:
        x = 'Hybrid Sampling'
    elif linear_constant_growth:
        x = 'Linear Constant Sampling'
    elif exponential_constant_growth:
        x = 'Exponential Constant Sampling'
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%, {x}",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(output_dir, 'query_times_boxplot.png'))
    plt.close()



def plot_query_times_boxplot_all(all_connections_query_time, output_dir):
    """Plot boxplots for query times across all connection ranges and save them in a single figure."""

    plt.figure(figsize=(14, 7))
    plt.boxplot(all_connections_query_time, patch_artist=True, boxprops=dict(facecolor="lightblue"))
    plt.title(f"Query Times for Different Connection Ranges", fontsize=16)
    plt.ylabel("Query Time (seconds)", fontsize=16)
    plt.xlabel("Connection Ranges", fontsize=16)
    plt.xticks(ticks=range(1, len(connections_per_peer) + 1), 
               labels=[f"{conn[0]}-{conn[1]}" for conn in connections_per_peer])
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.axhline(y=12, color='red', linestyle='--', linewidth=1)
    plt.subplots_adjust(top=0.85)
    x = ''
    if exponential_growth:
        x = 'Exponential Sampling'
    elif linear_growth:
        x = 'Linear Sampling'
    elif hybrid_growth:
        x = 'Hybrid Sampling'
    elif linear_constant_growth:
        x = 'Linear Constant Sampling'
    elif exponential_constant_growth:
        x = 'Exponential Constant Sampling'
    plt.figtext(
        0.3, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%, {x}",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'query_times_all_connections_boxplot.png'))
    plt.close()




def plot_query_results_all(all_connections_query_results, exec_dir):
    """Plot pie charts in the same figure for block availability across multiple connection ranges."""
    num_ranges = len(connections_per_peer)
    fig, axes = plt.subplots(1, num_ranges, figsize=(6 * num_ranges, 7))

    for idx in range(num_ranges):
        connection_range = connections_per_peer[idx]
        range_label = f"{connection_range[0]}-{connection_range[1]}"
        connection_results = all_connections_query_results[idx]
        available_count = connection_results.count('success')
        not_available_count = connection_results.count('failure')
        sizes = [available_count, not_available_count]
        colors = ['lightgreen', 'salmon']
        ax = axes[idx]
        wedges, texts, autotexts = ax.pie(
            sizes, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 16}
        )
        for autotext in autotexts:
            autotext.set_fontsize(16)
        ax.set_title(f"Connection Range: {range_label}", fontsize=16)

    plt.subplots_adjust(top=0.9)
    x = ''
    if exponential_growth:
        x = 'Exponential Sampling'
    elif linear_growth:
        x = 'Linear Sampling'
    elif hybrid_growth:
        x = 'Hybrid Sampling'
    elif linear_constant_growth:
        x = 'Linear Constant Sampling'
    elif exponential_constant_growth:
        x = 'Exponential Constant Sampling'
    plt.figtext(
        0.3, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%, {x}",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    os.makedirs(exec_dir, exist_ok=True)
    output_path = os.path.join(exec_dir, 'query_results_pie_charts_all_ranges.png')
    plt.savefig(output_path)
    plt.close()


    



def count_malicious_peers(peerID_index, peer_id, peer_connections, peer_poison_map):
    level_1_peers = peer_connections.get(peer_id, [])
    
    level_2_peers = set()
    for level_1_peer in level_1_peers:
        level_2_peers.update(peer_connections.get(level_1_peer, []))
    
    level_2_peers.difference_update(level_1_peers)
    level_2_peers.discard(peer_id)
    
    malicious_level_1 = [peer for peer in level_1_peers if peer_poison_map.get(peer, 0) == 1]
    num_malicious_level_1 = len(malicious_level_1)
    
    # Count malicious Level 2 peers
    malicious_level_2 = [peer for peer in level_2_peers if peer_poison_map.get(peer, 0) == 1]
    num_malicious_level_2 = len(malicious_level_2)
    
    print(f"Peer {peerID_index} has : ")
    print(f"Malicious Level 1 Peers: {len(malicious_level_1)}")
    print(f"Malicious Level 2 Peers: {len(malicious_level_2)}")
    
    return num_malicious_level_1, num_malicious_level_2



def count_poisonous_nodes(peer_connections, peer_poison_map):
    level_1_poisonous_counts = []
    level_2_poisonous_counts = []

    for peer, level_1_peers in peer_connections.items():
        # Count poisonous Level 1 peers
        level_1_poisonous_count = sum(1 for p in level_1_peers if peer_poison_map.get(p, 0) == 1)
        
        # Find Level 2 peers by checking connections of Level 1 peers, excluding the original peer and Level 1 peers
        level_2_peers = set()
        for p in level_1_peers:
            level_2_peers.update(peer_connections.get(p, []))
        level_2_peers -= set(level_1_peers)
        level_2_peers.discard(peer)
        
        # Count poisonous Level 2 peers
        level_2_poisonous_count = sum(1 for p in level_2_peers if peer_poison_map.get(p, 0) == 1)

        # Append counts to the respective arrays
        level_1_poisonous_counts.append(level_1_poisonous_count)
        level_2_poisonous_counts.append(level_2_poisonous_count)

    return level_1_poisonous_counts, level_2_poisonous_counts


def plot_poisonous_counts(all_level_1_poisonous_counts, all_level_2_poisonous_counts, connection_ranges, exec_dir):
    os.makedirs(exec_dir, exist_ok=True)
    labels = [f"{r[0]}-{r[1]}" for r in connection_ranges]
    
    plt.figure(figsize=(14, 7))
    plt.boxplot(all_level_1_poisonous_counts, labels=labels)
    plt.title("Level 1 Poisonous Node Count", fontsize=16)
    plt.xlabel("Connections Per Peer Range", fontsize=16)
    plt.ylabel("Number of Poisonous Nodes", fontsize=16)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(exec_dir, "level_1_poisonous_counts.png"))
    plt.close()

    # Plot for Level 2 poisonous counts
    plt.figure(figsize=(14, 7))
    plt.boxplot(all_level_2_poisonous_counts, labels=labels)
    plt.title("Level 2 Poisonous Nodes Count", fontsize=16)
    plt.xlabel("Connections Per Peer Range", fontsize=16)
    plt.ylabel("Number of Poisonous Nodes", fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    plt.subplots_adjust(top=0.9)
    plt.figtext(
        0.2, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    plt.savefig(os.path.join(exec_dir, "level_2_poisonous_counts.png"))
    plt.close()


def plot_original_retries_boxplot_all(all_connections_original_retries, output_dir):
    """Plot boxplots for original retries across all connection ranges and save them in a single figure."""
    
    plt.figure(figsize=(14, 7))
    # all_connections_original_retries = [[val + 1 for val in retry_list] for retry_list in all_connections_original_retries]
    plt.boxplot(all_connections_original_retries, patch_artist=True, boxprops=dict(facecolor="lightgreen"))
    
    plt.title("Number of peers queried by each node for a sample across connection ranges", fontsize=16)
    plt.ylabel("Count of Queried Peers", fontsize=16)
    plt.xlabel("Connection Ranges", fontsize=16)
    plt.xticks(ticks=range(1, len(connections_per_peer) + 1),
               labels=[f"{conn[0]}-{conn[1]}" for conn in connections_per_peer],
               fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    x = ''
    if exponential_growth:
        x = 'Exponential Sampling'
    elif linear_growth:
        x = 'Linear Sampling'
    elif hybrid_growth:
        x = 'Hybrid Sampling'
    elif linear_constant_growth:
        x = 'Linear Constant Sampling'
    elif exponential_constant_growth:
        x = 'Exponential Constant Sampling'
    plt.figtext(
        0.3, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%, {x}",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'original_retries_all_connections_boxplot.png'))
    plt.close()


def plot_all_connections_all_retries_sum_per_node_boxplot(all_connections_all_retries_sum_per_node, output_dir):
    plt.figure(figsize=(14, 7))
    plt.boxplot(all_connections_all_retries_sum_per_node, patch_artist=True, 
                boxprops=dict(facecolor="lightgreen"))
    plt.title("Total Sampling Requests Sent by Each Node", fontsize=16)
    plt.ylabel("Sum of all sampling requests for each node", fontsize=16)
    plt.xlabel("Connection Ranges", fontsize=16)
    plt.xticks(ticks=range(1, len(connections_per_peer) + 1),
               labels=[f"{conn[0]}-{conn[1]}" for conn in connections_per_peer],
               fontsize=16)
    plt.grid(True, axis='y', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='major', labelsize=16)
    x = ''
    if exponential_growth:
        x = 'Exponential Sampling'
    elif linear_growth:
        x = 'Linear Sampling'
    elif hybrid_growth:
        x = 'Hybrid Sampling'
    elif linear_constant_growth:
        x = 'Linear Constant Sampling'
    elif exponential_constant_growth:
        x = 'Exponential Constant Sampling'
    plt.figtext(
        0.3, 0.96,
        f"Validator custody: {val_custody}, Malicious nodes: {poison_percentage}%, {x}",
        fontsize=16,
        ha='center',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round')
    )
    output_path = os.path.join(output_dir, 'retries_sum_boxplot_per_node.png')
    plt.savefig(output_path)
    plt.close()



def main():
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Generate unique execution ID based on current date and time
    exec_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    exec_dir = os.path.join(results_dir, exec_id)
    os.makedirs(exec_dir)
    
    csv_file = 'transformed_node_data.csv'

    print("Starting the program...")

    # load csv files
    peerIDs, node_data, todes_data = load_node_data(csv_file)

    peerID_to_val = map_peerIDs_to_values(peerIDs, node_data)
    
   
    if not poison_by_percentage:
        peer_poison_map = mark_poisoned_nodes(peerIDs, node_data, todes_data)
    else:
        peer_poison_map = mark_poisoned_nodes_by_percentage(peerIDs)
    
    peer_custody, row_custody, col_custody = assign_rows_cols(peerIDs, node_data)

    
    
    plot_custody_distribution(row_custody, col_custody, peer_poison_map, exec_dir)
    plot_custody_distribution_boxplot(row_custody, col_custody, peer_poison_map, exec_dir)

    plot_node_cells_downloaded(node_data, exec_dir)
    plot_node_data(node_data, exec_dir)
    

    horizon_data = []
    horizon_data_cells = []
    horizon_data_level_2 = []
    horizon_data_cells_level_2 = []
    cell_count_summary = [] 
    cell_count_summary_without_poisonous_nodes = []
    all_connections_query_time = []
    all_connections_original_retries = []
    all_connections_query_results = []
    all_connections_all_retries_sum_per_node = []
    all_level_1_poisonous_counts = []
    all_level_2_poisonous_counts = []

    selected_index = random.randint(0, len(peerIDs) - 1)
    selected_node = peerIDs[selected_index]
    
    for connections in connections_per_peer:

        peer_connections = connect_peers(peerIDs, connections)

        level_1_poisonous_counts, level_2_poisonous_counts = count_poisonous_nodes(peer_connections, peer_poison_map)
        all_level_1_poisonous_counts.append(level_1_poisonous_counts)
        all_level_2_poisonous_counts.append(level_2_poisonous_counts)

        # Create the directory for each connection
        output_dir = os.path.join(exec_dir, 'connections', f'{connections}')
        os.makedirs(output_dir, exist_ok=True)
        
        peer_horizon = calculate_horizon(peer_custody, peer_connections, peer_poison_map)
        peer_horizon_level_2 = calculate_horizon_level_2(peer_custody, peer_connections, peer_poison_map)

        
        level_1_supernodes_count, level_2_supernodes_count = calculate_supernode_distribution(peer_connections, peerID_to_val)
        plot_supernode_distribution(level_1_supernodes_count, level_2_supernodes_count, connections, output_dir)

        # Plotting results in the specific directory
        plot_horizon_distribution(peer_horizon, output_dir)
        
        horizon_rows = [
            len(peer_horizon.get(peer, {'rows': set()})['rows']) if len(peer_horizon.get(peer, {'rows': set()})['rows']) < num_rows / 2 else num_rows
            for peer in peerIDs if peer_poison_map.get(peer) != 1
        ]

        horizon_cols = [
            len(peer_horizon.get(peer, {'cols': set()})['cols']) if len(peer_horizon.get(peer, {'cols': set()})['cols']) < num_cols / 2 else num_cols
            for peer in peerIDs if peer_poison_map.get(peer) != 1
        ]

        horizon_data.append({
            'rows': horizon_rows,
            'cols': horizon_cols
        })

        horizon_cells = calculate_horizon_cells(peer_horizon)
        horizon_data_cells.append(horizon_cells)

        plot_peer_coverage(selected_node, peer_connections, peer_custody, peer_poison_map, output_dir)

        cell_count, cell_count_without_poisonous_nodes = calculate_peer_coverage_cells(selected_node, peer_connections, peer_custody, peer_poison_map)
        cell_count_summary.append(cell_count)
        cell_count_summary_without_poisonous_nodes.append(cell_count_without_poisonous_nodes)
        plot_peer_coverage_cells(cell_count, output_dir)
        plot_peer_coverage_cells_without_poisonous_nodes(cell_count_without_poisonous_nodes, output_dir)
        
        # plot_peer_coverage_cells_all(peerIDs, peer_connections, peer_custody, output_dir)

        horizon_rows_level_2 = [
            len(peer_horizon_level_2.get(peer, {'rows': set()})['rows']) if len(peer_horizon_level_2.get(peer, {'rows': set()})['rows']) < num_rows / 2 else num_rows
            for peer in peerIDs if peer_poison_map.get(peer) != 1
        ]

        horizon_cols_level_2 = [
            len(peer_horizon_level_2.get(peer, {'cols': set()})['cols']) if len(peer_horizon_level_2.get(peer, {'cols': set()})['cols']) < num_cols / 2 else num_cols
            for peer in peerIDs if peer_poison_map.get(peer) != 1
        ]

        horizon_data_level_2.append({
            'rows': horizon_rows_level_2,
            'cols': horizon_cols_level_2
        })

        horizon_cells_level_2 = calculate_horizon_cells_level_2(peer_horizon_level_2)
        horizon_data_cells_level_2.append(horizon_cells_level_2)

        all_query_times, all_results, all_original_retries, all_retries_sum_per_node = query_all_nodes(peerIDs, peer_custody, peer_connections, peer_horizon, peer_horizon_level_2, peer_poison_map)
        all_connections_query_time.append(all_query_times)
        all_connections_query_results.append(all_results)
        all_connections_original_retries.append(all_original_retries)
        all_connections_all_retries_sum_per_node.append(all_retries_sum_per_node)
        plot_query_times_boxplot(all_query_times, connections, output_dir)


    plot_query_times_boxplot_all(all_connections_query_time, exec_dir)
    plot_query_results_all(all_connections_query_results, exec_dir)
    plot_original_retries_boxplot_all(all_connections_original_retries, exec_dir)
    plot_all_connections_all_retries_sum_per_node_boxplot(all_connections_all_retries_sum_per_node, exec_dir)
    

    file_name_retries = "retries_sum_per_node.json"
    file_name_query_time = "query_time_per_node.json"
    file_path_retries = os.path.join(exec_dir, file_name_retries)
    file_path_query_time = os.path.join(exec_dir, file_name_query_time)

    with open(file_path_retries, "w") as file:
        json.dump(all_connections_all_retries_sum_per_node, file)

    with open(file_path_query_time, "w") as file:
        json.dump(all_connections_query_time, file)



    plot_cell_count_without_poisonous_nodes_boxplot(cell_count_summary_without_poisonous_nodes, exec_dir)
    plot_poisonous_counts(all_level_1_poisonous_counts, all_level_2_poisonous_counts, connections_per_peer, exec_dir)

    # Level 1 horizon boxplots
    plot_horizon_distribution_boxplot(horizon_data, exec_dir)
    plot_horizon_cells_distribution_boxplot(horizon_data_cells, exec_dir)
    # print_horizon_statistics(horizon_data)
    # print_horizon_cells_statistics(horizon_data_cells, connections_per_peer)


    # Level 2 horizon boxplots
    plot_horizon_distribution_boxplot_level_2(horizon_data_level_2, exec_dir)
    plot_horizon_cells_distribution_boxplot_level_2(horizon_data_cells_level_2, exec_dir)
    # print_horizon_cells_statistics(horizon_data_cells_level_2, connections_per_peer)

    # sys.stdout.log.close()
    # sys.stdout = sys.__stdout__

    print("Program finished.")
    

if __name__ == "__main__":
    main()
