<%inherit file="/loggedin.mako" />

<div class="row">
    %for integration in integration_list:
    <div class="col-md-2">
        <div class="thumbnail">
            <img src="${ integration.get_service().get_logo_path() }" alt="${ integration.name|h }" width="150" height="150">
            <div class="caption">
                <p>${ integration.name|h }</p>
                <p>
                    <div class="btn-group btn-group-justified">
                        <a href="/integrations/${ integration.get_service().id|h }/${ integration.id }/edit"
                           class="btn btn-primary"
                           role="button">Edit</a>
                        <a href="/integrations/${ integration.get_service().id|h }/${ integration.id }/delete"
                           class="btn btn-danger"
                           role="button">Delete</a>
                    </div>
                </p>
            </div>
        </div>
    </div>
    %endfor
    <div class="col-md-2">
        <div class="thumbnail">
            <img src="/static/common/default_logo.png" alt="New integration" width="150" height="150">
            <div class="caption">
                <p>&nbsp;</p>
                <p>
                    <a href="/services"
                       class="btn btn-success btn-block"
                       role="button"><span class="glyphicon glyphicon-plus"></span> New Integration</a>
                </p>
            </div>
        </div>
    </div>
</div>

<!--
<h2>Services</h2>

<div class="row">
    %for service in service_list:
    <div class="col-md-2">
        <div class="thumbnail">
            <img src="${ service.get_logo_path() }" alt="${ service.name|h }" width="150" height="150">
            <div class="caption">
                <p>${ service.name|h }</p>
                <p>
                    <a href="/integrations/${ service.id|h }/add"
                       class="btn btn-primary"
                       role="button">Add integration</a>
                </p>
            </div>
        </div>
    </div>
    %endfor
</div>
-->
