经常构建docker 镜像的时候，在镜像Build时需要经常软件的安装或更新时，运行apt-get update 或者apt-get install 时出现Temporary failure resolving 'security.ubuntu.com'报错时，修改如下可以解决

```bash
cd /etc/docker
touch daemon.json
```
然后将如下的内容放入daemon.json里面


```bash
{                                                                          
    "dns": ["8.8.8.8", "114.114.114.114"]                                                                           
}  
``` 
重启docker

```bash
sudo systemctl restart docker
```