import pandas as pd
from GenerateLexDir import literal_eval_col

in_file = 'merge_matches.csv'

def main():
    df = pd.read_csv(in_file, keep_default_na=False, index_col='entry_id')
    df.to_csv('merge_matchesOLD.csv')
    literal_eval_col(df, 'matches')
    print(len(df))
    
    processed = ['merge' in x for x in df['status']]
    unprocessed = [not x for x in processed]
    processed = df[processed]
    unprocessed = df[unprocessed]

    processed_ids = list(processed.index)
    for m in processed['matches']:
        processed_ids.extend( m.keys() )
    
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