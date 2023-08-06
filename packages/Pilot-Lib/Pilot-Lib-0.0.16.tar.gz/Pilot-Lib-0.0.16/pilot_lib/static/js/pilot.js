
var Pilot = {

    trackEvent: function(category, action, label, value) {
        if (typeof ga !== 'undefined') {
            ga("send", "event", category, action, label, value)
        }
    },

    /**
    Social Login
    Use hello.js for front end authentication
    **/
    social_login: function(config) {
        hello.init(config, {redirect_uri: 'redirect.html'})

        $("[pilot\\:social-login]").click(function(){
            var el = $(this)
            var form = el.closest("form")
            var status = form.find(".status-message")

            var provider = el.attr("pilot:social-login")
            if (provider == "google-plus") {
                provider = "google"
            }

            hello(provider).login({"force": true}).then( function(){

                hello(provider).api( '/me' ).then( function(r){

                    status.addClass("alert alert-success").html("Siging in... ")

                    console.log(r.name)
                    console.log(r.id)
                    console.log(r.email)
                    console.log(r.thumbnail)
                    console.log(r)

                    var image_url = r.thumbnail
                    if ( provider === "facebook" ) {
                        image_url += "?type=large"
                    }
                    console.log(image_url)
                    form.find("[name='provider']").val(provider)
                    form.find("[name='provider_user_id']").val(r.id)
                    form.find("[name='name']").val(r.name)
                    form.find("[name='email']").val(r.email)
                    form.find("[name='image_url']").val(image_url)

                    Pilot.trackEvent("Login", "Social Login Button", provider)
                    //form.submit()
                });

            }, function( e ){

                var error_message = ""

            });

        })
    }

}
