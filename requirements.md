# 项目名称
阿里云云资源管理服务

# 架构设计
- 采用docker compose技术构架容器化web api服务
- docker image需要根据运行的环境选择arm64或amd64两个构架来生成image
- 使用python fastapi框架
- 对外监听服务端口6060
- 相关配置参数在compose.yml里定义，如访问阿里云资源的ak参数：ACCESS_KEY_ID和ACCESS_KEY_SECRET，以及IP白名单
- 所有代码执行均要在docker容器内部

# 功能需求
- 要有白名单保护机制，避免一些白名单IP被误封，白名单IP：100.127.0.0/16,172.0.0.0/24,120.26.104.119,118.178.225.60,120.55.114.170,47.97.35.133,8.211.48.57,159.75.166.147,106.52.33.85,47.96.105.237,47.96.74.52
- 需要有测试用例，保证接口调用正常,可以用IP 34.1.28.44 进行测试
- 开发接口时你可以参考项目目录下ecs-acl-demo和alb-acl-demo的代码，这是从阿里云SDK下载的示例
- 接口操作要有详情的log记录，包括请求时间，ip，接口响应状态等

# API接口需求
- 添加ALB访问控制条目
- 删除ALB访问控制条目
- 增加ECS安全组入方向规则
- 删除ECS安全组入方向规则

# API具体定义
- 添加ALB访问控制条目
接口名称：
AddEntriesToAcl

参数：
SourceCidrIp - 来源ip地址，如192.168.1.0/24，对应接口文档的Entry字段
Description - 描述，默认：{添加日期和时间}

接口文档：
https://help.aliyun.com/zh/slb/application-load-balancer/developer-reference/api-alb-2020-06-16-addentriestoacl?spm=a2c4g.11186623.help-menu-27537.d_4_0_4_10_0.5ef13f69FdkVnH&scm=20140722.H_2254785._.OR_help-T_cn~zh-V_1

接口说明：

- 删除ALB访问控制条目
接口名称：
RemoveEntriesFromAcl

参数：
SourceCidrIp - 来源ip地址，如192.168.1.0/24，对应接口文档的Entry字段

接口文档：
https://help.aliyun.com/zh/slb/application-load-balancer/developer-reference/api-alb-2020-06-16-removeentriesfromacl?spm=a2c4g.11186623.help-menu-27537.d_4_0_4_10_9.740c4104Yv5Tz5&scm=20140722.H_2254815._.OR_help-T_cn~zh-V_1

接口说明：
SourceCidrIp采用单条移除访问控制条目。

- 增加ECS安全组入方向规则
接口名称：
AuthorizeSecurityGroup

参数：
RegionId - 地区id，默认值cn-hangzhou
SourceCidrIp - 来源ip地址，如192.168.1.0/24
SecurityGroupI - 安全组规则名称，默认值sg-bp19nke7purenpearpmb
Policy - 出入站规则，可选值drop/accept，默认drop
PortRange - 端口范围，如22/22，默认值-1/-1
IpProtocol - 协议，默认ALL

接口文档：
https://help.aliyun.com/zh/ecs/developer-reference/api-ecs-2014-05-26-authorizesecuritygroup?spm=a2c4g.11186623.help-menu-25365.d_1_0_4_10_6.5c8d1e4b10b5gg&scm=20140722.H_2679850._.OR_help-T_cn~zh-V_1

接口说明：

- 删除ECS安全组入方向规则
接口名称：
RevokeSecurityGroup

参数：
SourceCidrIp -  来源ip地址，如192.168.1.0/24
SecurityGroupI - 安全组规则名称，默认值sg-bp19nke7purenpearpmb
Policy - 出入站规则，可选值drop/accept，默认drop
PortRange - 端口范围，如22/22，默认值-1/-1
IpProtocol - 协议，默认ALL

接口文档：
https://help.aliyun.com/zh/ecs/developer-reference/api-ecs-2014-05-26-revokesecuritygroup?spm=a2c4g.11186623.help-menu-25365.d_1_0_4_10_8.2493d6f7D47yg4&scm=20140722.H_2679855._.OR_help-T_cn~zh-V_1

接口说明：
通过指定 Permissions 删除规则

# AI提示词
- 现在需要创建一个管理aliyun的docker服务运行的服务。需求：1、使用docker compose； 2、运行flask，监听端口6060；3、添加4个服务接口：AddEntriesToAcl - 添加访问控制条目、RemoveEntriesFromAcl - 移除访问控制条目、AuthorizeSecurityGroup - 增加安全组入方向规则、RevokeSecurityGroup - 删除安全组入方向规则。 具体定义请参考需求文档 @requirements.md ，先不要直接开发，要先制定计划，确认后再开发
- 相关python环境的检查要在docker里检查，不要检查容器外的情况
- python要使用中国国内镜像源进行依赖包的安装
- 所有代码执行均要在docker容器内部
- 所有代码执行均要在docker容器内部
- 所有代码执行均要在docker容器内部
- 要及时删除没用的测试文档和代码
- 项目开发结束后要及时删除没用的测试文档和代码