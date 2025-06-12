import pandas as pd
import argparse
import os
import re


def combine_results(results_dir, batch_csv_path, quantification_path, output_dir):
    batch_csv = pd.read_csv(batch_csv_path)
    quantification = pd.read_csv(quantification_path)
    dfs = []
    for anot_filename in os.listdir(results_dir):
        match = re.search(r'_annotation_(\d+)\.csv$', anot_filename)
        if match:
            index_from_file = int(match.group(1))
            print(f"Processing annotation file: {anot_filename} for index: {index_from_file}")
            annotation = pd.read_csv(os.path.join(results_dir, anot_filename))
            annotation = annotation.rename(columns={'Cell Index': 'cell_id', 'Cell Type': 'predicted_phenotype'})
            image_path_string = batch_csv['image_path'][index_from_file]
            image_name = os.path.basename(image_path_string)
            annotation['unique_id'] = image_name + '_' + annotation['cell_id'].astype(str)
            annotation['predicted_phenotype'] = annotation['predicted_phenotype'].replace({'B cell': 'B_cell', 'Others': 'undefined', 'Dendritic cell': 'Dendritic_cell', 'CD8 T cell': 'CD8+_T_cell', 'CD4 T cell': 'CD4+_T_cell',
                                                'M2 macrophage cell': 'M2_Macrophage', 'M1 macrophage cell': 'M1_Macrophage', 'Natural killer cell': 'NK_cell',
                                                'Plasma cell': 'Plasma_cell', 'Regulatory T cell': 'Treg', 'Granulocyte cell': 'Neutrophil', 'Mast cell': 'Mast_cell',
                                                'Endothelial cell': 'Endothelial', 'Epithelial cell': 'Epithelial', 'Proliferating/tumor cell': 'Cancer', 'Smooth muscle': 'Stromal',
                                                'Stroma cell': 'Stromal'})
            dfs.append(annotation[['unique_id', 'predicted_phenotype']])
    df = pd.concat(dfs, ignore_index=True)
    quantification['unique_id'] = quantification['image'] + '_' + quantification['cell_id'].astype(str)
    result = pd.merge(quantification, df, on='unique_id', how='left')
    result = result.rename(columns={'cell_type': 'true_phenotype'})
    result.drop(columns=['unique_id'], inplace=True)
    result['predicted_phenotype'] = result['predicted_phenotype'].fillna('undefined')
    result.to_csv(os.path.join(output_dir, 'predictions.csv'), index=False)

def main():
    parser = argparse.ArgumentParser(description="Combine results from ribca output files.")
    parser.add_argument("--results_dir", type=str, required=True, help="Path to the directory containing ribca annotation results.")
    parser.add_argument("--batch_csv_path", type=str, required=True, help="Path to the batch CSV file.")
    parser.add_argument("--quantification_path", type=str, required=True, help="Path to the quantification CSV file.")
    parser.add_argument("--output_dir", type=str, required=True, help="Path to the output directory for combined results.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    combine_results(args.results_dir, args.batch_csv_path, args.quantification_path, args.output_dir)

if __name__ == "__main__":
    main()