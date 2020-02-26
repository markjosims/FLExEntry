{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "# header\n",
    "import pandas as pd\n",
    "from GenerateLexDir import literal_eval_col"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# load in data\n",
    "flexicon = pd.read_csv('FlexiconMERGE.csv', index_col='entry_id', keep_default_na=False)\n",
    "merges = pd.read_csv('merge_matches.csv', index_col='entry_id', keep_default_na=False)\n",
    "#merge merge merge merg mregggg\n",
    "\n",
    "# take things literally\n",
    "literal_eval_col(merges, 'matches')\n",
    "\n",
    "literal_eval_col()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.4"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
