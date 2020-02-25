import pandas as pd
import os

# Relative path to folder containing samples
prefix = '../../Projekat_1/'

groups = [['GSM3087619', 'GSM3478792', 'GSM3892570', 'GSM3892571', 'GSM3169075'],
          ['GSM3087622', 'GSM3087624', 'GSM3087626'],
          ['GSM3892572', 'GSM3892573', 'GSM3892574', 'GSM3892575', 'GSM3892576'],
          ['GSM2560245', 'GSM2560246', 'GSM2560247', 'GSM2560248', 'GSM2560249']]


def join(p1, p2):
    return os.path.join(p1, p2)


def get_filename(folder):
    path = join(prefix, folder)
    csv = [file for file in os.listdir(path) if file.endswith('.csv')]
    filename = csv[0]
    return filename


common_human_list = pd.read_csv(join(prefix, 'common_human_list.csv'))
genome_sample = pd.read_csv(join(prefix, 'SCT-10x-Metadata_readylist_merged-PBMC-tasks-short-Bgd.csv'))

ENSG_IDs = list(common_human_list['ENSG_ID'])


def transpose(data, sample):
    data_t = data.set_index('Index').transpose()
    data_t.index = new_index(data_t.shape, sample)
    return data_t


def new_index(shape, sample):
    index = [str(sample) + '_' + str(i + 1) for i in range(shape[0])]
    return index


# Dropping ENSG_IDs which are not ni common_human_list
def drop_invalid_ensg(df):
    return df[df['Index'].isin(ENSG_IDs)]


# Dropping genes in raw data
# currently unused
def drop_rows(df, threshold):
    percentage = threshold / 100.0
    df.drop(df[(df.iloc[:, 1:] > 0).sum(axis=1) / (len(df.columns) - 1) < percentage].index, inplace=True)


# Dropping genes after transposing
# threshold is in percents
def drop_genes(df, threshold):
    print(f'\tDropping genes...')
    percentage = threshold / 100.0

    dropping = df.columns[(df > 0).sum() / len(df.columns) < percentage]
    df.drop(columns=dropping, inplace=True)


# Dropping cells in raw data
# threshold_1 = min number of positive values
# threshold_2 = min sum
def drop_cells(df, threshold_1, threshold_2):
    columns = df.columns[1:]
    dropping = columns[((df.iloc[:, 1:] > 0).sum() < threshold_1) | (df.iloc[:, 1:].sum() < threshold_2)]
    df.drop(columns=dropping, inplace=True)


def prepare(sample):
    print(f'\tParsing {sample}')
    data = pd.read_csv(join(prefix, sample) + '/' + get_filename(sample))

    data = drop_invalid_ensg(data)

    # drop cells
    drop_cells(data, 500, 1000)

    # transpose
    data = transpose(data, sample)

    return data


def main():
    for i, group in enumerate(groups):
        group_id = f'group_{i + 1}'
        print(group_id)
        dfs = [prepare(sample) for sample in group]

        # at this point we have list with dropped invalid genes, and cells
        # then, we should concat all dataframes in dfs list
        # after concat, genes should be dropped
        # lastly, that big df should be saved on disk, in folder named after group, group_1, group_2 etc.

        resulting = pd.concat(dfs, sort=False)

        drop_genes(resulting, 1.0)

        os.mkdir(join('../data', group_id))
        print(f'\tShape after parsing: {resulting.shape}')
        print(f'\tSaving on path ../data/{group_id}/data.csv')
        resulting.to_csv(join('../data', group_id) + '/data.csv')

        # TODO remove break when preprocessing all groups
        break


if __name__ == '__main__':
    main()