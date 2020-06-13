from .utils import mybuild_dataset, build_iterator
from .models import TextRNN as x

# from utils import mybuild_dataset, build_iterator
# from models import TextRNN as x
from importlib import import_module
import torch
import numpy as np
import os
def get_sentiment(comments):
    current_work_dir = os.path.dirname(__file__)
    dataset = current_work_dir+'/static'  # 数据集
    model_name='TextRNN'
    
    # x = import_module(current_work_dir+'.models.' + model_name)
    config = x.Config(dataset, None)

    vocab,test_data = mybuild_dataset(config, True,comments)
    test_iter = build_iterator(test_data, config)

    # train
    config.n_vocab = len(vocab)
    model = x.Model(config).to(config.device)

    model.load_state_dict(torch.load(config.save_path))
    model.eval()

    predict_all = np.array([], dtype=int)

    neg_count,total_count=0,0
    with torch.no_grad():
        for texts, labels in test_iter:
            outputs = model(texts)
            predic = torch.max(outputs.data, 1)[1].cpu().numpy()
            _, predicted = torch.max(outputs.data, dim=1)
            total_count += labels.size(0)
            neg_count += (predicted == 0).sum().item()

    pos_count=total_count-neg_count

    pos_number_ratio = 100*pos_count//total_count 
    neg_number_ratio = 100*neg_count//total_count

    result_dict={
        'positive_rate':str(pos_number_ratio)+'%',
		'negative_rate':str(neg_number_ratio)+'%',
		'pos_count':pos_count,
		'neg_count':neg_count,
		'total_count':total_count
    }

    return result_dict

if __name__=='__main__':
    comments={"你好","我好","大家好","我很伤心"}
    print(get_sentiment(comments))

