<%inherit file="/base.mako" />

<%block name="navbar">

    <ul class="nav navbar-nav">
        <li ${ 'class="active"' if active == 'dashboard' else '' }><a href="/">Dashboard</a></li>
        <li ${ 'class="active"' if active == 'services' else '' }><a href="/services">Services</a></li>
    </ul>

    <ul class="nav navbar-nav navbar-right">
        <li><a href="/logout">Logout</a>
    </ul>
    <p class="navbar-text navbar-right">
        <span class="glyphicon glyphicon-user"></span>
        ${ user.email|h }
    </p>
</%block>
