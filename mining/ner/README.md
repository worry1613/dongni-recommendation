# 命名实体识别
data  
此目录存放 人民日报1998年1月已标注数据集。  
model  
此目录存放已经训练好的模型，可以直接使用。    
模型文件下载链接:https://pan.baidu.com/s/1t8dHEIsWmfUGQO6xbadhIA  密码:hln7   
corpus.py  
处理数据集，标注格式，生成可供CRF++训练和测试的数据集。  
nerpredit.py  
用训练好的模形预测NER内容。此文件只在python3环境下测试通过。  

**nerpredit.py只在python3环境下测试通过**