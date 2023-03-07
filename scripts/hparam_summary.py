"""
Usage:
    python scripts/hparam_summary.py --dir configs

To exclude hyperparameters that we don't care from the result table, please add them to `dont_care` list.
"""

import sys
sys.path.append('.')

import glob
import os
import pandas as pd
import yaml
import argparse

#mode = 'new'
#assert mode in ['append', 'new'], 'Not valid'
#output_path = './hparams.xlsx'
config_dir = './configs'
dont_care = ['distribute', 'shuffle', 'val_while_train', 'dataset', 'data_dir', 'dataset_download',
                  'model', 'pretrained', 'ckpt_path', 'keep_checkpoint_max', 'save_checkpoint', 'ckpt_save_dir',
                  'data_url', 'device_target', 'train_split', 'val_split', 'in_channels', 'ckpt_save_interval',
                  'ckpt_save_policy', 'val_interval', 'log_interval']

#empty_fill = '-'


def main(config_dir, output_path):
    # get all yaml
    df = pd.DataFrame()
    recipes = sorted(glob.glob(f"{config_dir}/*/*.yaml"))
    print("Total number of training recipes: ", len(recipes))

    # convert yaml to data item
    for i, yaml_fp in enumerate(recipes):
        with open(yaml_fp) as fp:
            config  = yaml.safe_load(fp)
            #print(config.keys())
        #arch_name = config['model'] # cannot tell gpu from ascend
        arch_name = os.path.basename(yaml_fp).replace('.yaml', '').replace('.yml','')

        if arch_name in list(df.columns.values):
            print(arch_name + ' already exists, skipped')

        num_cols = len(list(df.columns.values)) # num of models recorded in table
        if num_cols == 0:
            hparams = [] #[k for k in config.keys() if k not in dont_care]
            hvals = []
            for k in config.keys():
                if k not in dont_care:
                    hparams.append(k)
                    hvals. append(config[k])
            df.insert(0, "hparam", hparams + ['yaml_path'])
            df.insert(1, arch_name, hvals + [yaml_fp])
        else:
            hvals = []
            for hp in hparams:
                if hp in config:
                    hvals.append(config[hp])
                else:
                    hvals.append('-')
            df.insert(num_cols, arch_name, hvals + [yaml_fp])

            # check new hparams
            cur_hparams = []
            ptr = 0 # pointer to the last matched location
            for k in config.keys():
                if k not in dont_care:
                    if k in hparams:
                        ptr = hparams.index(k)
                    if k not in hparams:
                        # insert a new row after ptr
                        row_values = [k] + ['-']*i + [config[k]]
                        df.loc[ptr+0.5] = row_values
                        df = df.sort_index().reset_index(drop=True)

                        # update hparams
                        hparams = hparams[:ptr+1] + [k] + hparams[ptr+1:]

    df.to_excel(output_path, index=False)
    print(f'Job completed. Result saved in {output_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hyper params summary', add_help=False)
    parser.add_argument('-d', '--dir', type=str, default='./configs',
                               help='directory to  the `configs` folder')
    parser.add_argument('-o', '--output_path', type=str, default='./hparam_summary.xlsx',
                               help='output path to save the result table')
    args = parser.parse_args()

    main(args.dir, args.output_path)



