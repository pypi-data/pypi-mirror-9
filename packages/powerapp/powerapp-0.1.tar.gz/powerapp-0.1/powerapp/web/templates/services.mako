<%inherit file="/loggedin.mako" />


<div class="row">
    %for service in service_list:
    <div class="col-md-2">
        <div class="thumbnail">
            <img src="${ service.get_logo_path() }" alt="${ service.name|h }" width="150" height="150">
            <div class="caption">
                <p>${ service.name|h }</p>
                <p>
                    <a href="/integrations/${ service.id|h }/add"
                       class="btn btn-success btn-block"
                       role="button">Add integration</a>
                </p>
            </div>
        </div>
    </div>
    %endfor
</div>
