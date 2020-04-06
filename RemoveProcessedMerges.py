import pandas as pd
from GenerateLexDir import literal_eval_col

in_file = 'merge_matches3_1.csv'

def main():
    df = pd.read_csv(in_file, keep_default_na=False, index_col='entry_id')
    df.to_csv('merge_matches3_1OLD.csv')
    print(len(df))
    
    merge = [x=='merge' for x in df['status']]
    ignore = [x=='ignore' for x in df['status']]
    unprocessed = [not x for x in df['status']]

    merge = df[merge]
    ignore = df[ignore]
    unprocessed = df[unprocessed]

    processed_ids = list(merge.index) + list(merge['match_id'])
    
    for id in processed_ids:
        if id in unprocessed.index:
            df = df.drop(id)
        
        idcs = [
                index for index, match in\
                zip(unprocessed.index, unprocessed['matches'])\
                if (id in match) and index in df.index
               ]
        
        for i in idcs:
            del df.at[i, 'matches'][id]
            assert id not in df.at[i, 'matches']
    
    not_empty = [bool(x) for x in df['matches']]
    df = df[not_empty]

    df.to_csv('merge_matches.csv')
    print(len(df))
    

if __name__ == '__main__':
    main()