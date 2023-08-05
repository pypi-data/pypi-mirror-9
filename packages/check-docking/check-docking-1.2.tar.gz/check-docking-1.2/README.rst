check-docking.

介绍:
-----

    此子项目仅为总结前项目的经验, 在后续项目上, 接口文档的定义入库, 结合入库的数据生成配置文件.

    根据生成的配置文件, 当客户端与服务端对接时, 让程序能够自动检查客户端的传入, 并将问题返回给客户端.

    该模块的目的在于减少客户端开发过程中, 在琐屑问题上对服务端的干扰. 如请求类型错误, 多参, 少参, 重参, 数据类型错误, 是否必填项等等.


使用:
-----

    配置settings.py修改：
        # check-docking配置项
            
            IS_DATA_INSPECT = True  # 仅 DEBUG 为 True 时有效
            
            INSPECT_PROFILE = "project.check_config"  # 检测依赖配置文件模块

        INSTALLED_APPS 增加:
            'check_docking',
            
            'check_docking.stored.django',

    下面两项非必须, 需要完成使用流程节点, 生成依赖的配置文件后启用其一.

        MIDDLEWARE_CLASSES 增加:
        
            'check_docking.middleware.InspectMiddleware'
            
        除了MiddleWare形式, 你也可以使用装饰器形式：
         
            from check_docking.inspect import debug_request
            
            ＠debug_request

    你还可以使用工具, 从源代码中搜集数据并入库, 具体可以参看project_demo/demo/demo.py中代码.


流程：
-------

        python manage.py syncdb
        
        python manage.py runserver
        
        http://127.0.0.0:8000/admin 录入数据.
        
        python manage.py inspectprofile

