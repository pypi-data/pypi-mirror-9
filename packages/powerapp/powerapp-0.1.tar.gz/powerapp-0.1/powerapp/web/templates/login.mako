<%inherit file="/base.mako" />

<div class="jumbotron login-box">
    <div class="container">
        <p>
            Welcome to Todoist PowerApps
        </p>
        <p>
            <a href="${ authorize_url|h }" class="btn btn-primary">Log in with your Todoist account</a>
        </p>
    </div>
</div>
