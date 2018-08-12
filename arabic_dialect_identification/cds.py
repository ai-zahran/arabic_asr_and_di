
# coding: utf-8

# In[50]:


import dialect_enrollment
import numpy as np
import operator
from sklearn.metrics import accuracy_score
import scipy
from utils.read_ivectors import read_ivectors_from_file, read_ivecs_set


# Read i-vectors for training and test data.

# In[2]:


train_ivecs_dir_path = '/home/ai/Projects/dialectID/data/train.vardial2017/whitened'
dev_ivecs_dir_path = '/home/ai/Projects/dialectID/data/dev.vardial2017/dev/normalized'
test_ivecs_file_path = '/home/ai/Projects/dialectID/data/dev.vardial2017/test/normalized'
dialects = ['EGY', 'GLF', 'LAV', 'MSA', 'NOR']


# In[3]:


train_ivecs = read_ivecs_set(train_ivecs_dir_path, dialects)
dev_ivecs = read_ivecs_set(dev_ivecs_dir_path, dialects)
test_ivecs = read_ivecs_set(test_ivecs_file_path, dialects)


# Compute dialect enrollment

# In[4]:


de_model = dialect_enrollment.model(train_ivecs.drop('utt-id',
    axis='columns'), dev_ivecs.drop('utt-id', axis='columns'))


# Compute cosine distance scores for the test set

# In[35]:


def cos_sim(X, Y):
    return 1 - scipy.spatial.distance.cosine(X, Y)


# In[51]:


predictions = test_ivecs.drop(['utt-id', 'dialect'], axis='columns').apply(
    lambda ivec: max((((dialect, cos_sim(de_model[dialect], ivec)))
    for dialect in de_model), key=operator.itemgetter(1))[0], axis='columns')


# In[52]:


accuracy_score(predictions, test_ivecs['dialect'])

