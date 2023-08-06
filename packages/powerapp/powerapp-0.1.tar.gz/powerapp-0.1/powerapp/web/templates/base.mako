<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title></title>
    <link rel="stylesheet" href="/static/common/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/common/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="/static/common/css/main.css">
    <script src="/static/common/js/jquery-1.11.2.min.js"></script>
    <script src="/static/common/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container">

    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <a href="/" class="pull-left"><img src="/static/common/powerapp50x50.png"
                                               style="max-height: 50px; padding: 0 30px 0 0;"
                                               alt="PowerApp"></a>
            <%block name="navbar"/>
        </div><!-- /.container-fluid -->
    </nav>

    ${self.body()}
</div>
</body>
</html>
