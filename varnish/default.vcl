vcl 4.1;

import dynamic;

backend default none;

sub vcl_init {
    new backend = director(port = "8000");
}

sub vcl_recv {
    set req.http.host = "revanced-releases-api";
    set req.backend_hint = backend.backend("revanced-releases-api");
}