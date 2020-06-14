## 源代码说明

实在是太大了，邮件发不了，我试着上传到我的github上，https://github.com/jlpang1997/GraduationDesign

WebProject是整个Django工程,两个情感分类器我都集成到里面去了

## 数据集说明

### 神经网络：WebProject\helloworld\Classification_Based_on_Networks

神经网络建立词汇表的文件是weibo_senti_100k.csv

训练集、验证集、测试集对应train.csv、dev.csv、test.csv

用到停用词为stop_words.txt

### 情感词典：WebProject\helloworld\Classification_Based_on_Sentiment_Dict

emotion_dict 对应情感词

degree_dict 对应程度副词

## 环境配置

python3.7(Anaconda)、Django、Pytorch(CPU)，主要用到的这两个，执行了如果不行的话，看缺少哪些包，爬虫我自己写了一个新的，放弃了框架。

windows10+vscode

mysql5.7

## 运行

没有服务器的话，直接本地运行，安装好所有模块之后，直接在WebProject目录下运行：

python manage.py runserver

然后在浏览器本地访问http://127.0.0.1:8000/index即可进入主页，然后网站的相关功能就可以一个一个看了。

## 一些说明

### 爬虫

由于项目用到爬虫，知乎和微博都需要会话控制，我用的是自己浏览器的cookie，所以，不保证师兄运行的时候依然有效。师兄可以去spiders.py目录替换对应的cookie字段（用自己的账号)。水木社区和百度贴吧没问题，师兄要是想爬得狠一些，可以修改spider对应的配置参数（废了人家服务器我不负责哈）。

### 网络

超参我前前后后调了好多次（主要是修改层数和轮数，还有就是pad_size)，所以ppt和毕业论文上面的测试精度都不一致，高了基本是因为轮数和层数增多了，低了是因为pad_size调大了,LSTM对长文本的效果确实不尽如人意。然后我现在提交的这一份，在static\saved_dict\TextRNN_acc.png会发现跟ppt里面的图又不一样，这个应该可以理解，神经网络嘛，炼丹效果……。

#### 参考文献

有两个英文文献我是看知网论文间接引用的，下不来对应的文本。我打包过去的论文里面有的我没有在论文里面引用，但毕设工作过程都看过，所以就全部打包发过去了。

#### 整个工程有点大，抱歉，师兄复现过程中遇到问题的话可以找我聊。

