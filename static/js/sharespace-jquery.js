$(document).ready(function() {

    ajax_user_query();
    console.log("page ready")



    $("#main_category").change(function(){
		const url = $("#add_item_form").attr("data-sub-cat-url");
		const catID = $(this).val();

		$.ajax({
			url : url,
			data: { 'main_category_id' : catID },
			success : function(data) {
				$("#sec_category").html(data);
			}
		});
	});

    $("#id_proposal_cat").change(function (){
        const url = $("#purchase_proposal_form").attr("data-sub-cat-url");
        const catID = $(this).val();
        console.log("cat element selected")

        $.ajax({
            url : url,
            data: {'main_category_id' : catID},
            success : function(data){
                $("#id_proposal_sub_cat").html(data);
            }

        });

    });

	$('#returned-item-btn').click(function(){
	    console.log("button in loan page clicked")
	    var loanSlugVar;
	    loanSlugVar = $(this).attr('data-loanslug');
        console.log("loan slug")
        console.log(loanSlugVar)
	    $.get('/sharespace/loan/return/',
	        {'loan_slug': loanSlugVar },
	        function(data){
	            $('#display-result').html("loan completed");
	            $('#returned-item-btn').hide();
	            console.log("ajax request done");
	        }
	    );

	});


     $('p').hover(
        function() {
            $(this).css('color', 'red');
        },
        function() {
            $(this).css('color', 'black');
        }
    );
});

function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

function ajax_user_query(){
    console.log("profile link func")
        const full_data = $("#profile-link").attr("data-username-url");
        console.log(full_data)
        const elems = full_data.split('-')
        console.log(elems[0], elems[1])
        url = elems[0]
        username = elems[1]
        $.ajax({
            url : url,
            data : {'username': username},
            success : function(data){
                console.log(data);

                set_elements(data);

            }
        });
}

function set_elements(data) {
    console.log("set element function");
    if (isEmpty(data)){
        console.log("anonymous user?");
    }

    else{

            console.log(data);
            console.log("in here");
            console.log(typeof data);
            console.log(data.img_path);
            console.log(data.user_url);

            const img_path = data.img_path;
            const profile_url = data.user_url;

            console.log(img_path);
            console.log(profile_url);

            var profile_link = document.getElementById("profile-link");
            profile_link.setAttribute("href", profile_url);

            var profile_icon = document.getElementById("profile-icon");
            console.log(profile_icon)
            profile_icon.setAttribute("src", img_path);


    }
}


function lookup_func() {
			console.log("post code function exec");
			var url = "https://api.getAddress.io/find/";
			var api_key = "IdUvLkdSBki8uOcIoH01EQ33123";
			var post_code = document.getElementById("add_item_postcode").value;
			var f_post_code = post_code.toLowerCase().replace(' ', '');
			console.log(f_post_code);
			var full_url = url + f_post_code + "?api-key=" + api_key;
			console.log("full url " + full_url)
			var request = new XMLHttpRequest();
			request.onreadystatechange = function(){
			    if(this.readyState == 4 && this.status == 200){
				    var myData = JSON.parse(this.responseText);
				    console.log("here is the data retrieved");
				    console.log(myData);
				    populate_list(myData);
			    }
			    else { console.log("error at request point" + request.status);
			    }
			};
			request.open("GET", full_url);
			request.send();
}

function populate_list(data) {
    const address_list = data['addresses'];
    var selection = document.getElementById("address_list");
    for (let i = 0; i< address_list.length; i++){
        var option = document.createElement("option");
        option.text = address_list[i];
        selection.add(option);
    }
}

function populate_address(){
    const sel_adr = document.getElementById("address_list");
    console.log(sel_adr.selectedIndex)
    var str_address = sel_adr.options[sel_adr.selectedIndex].text
    console.log(str_address)
    tokens = str_address.split(',')
    console.log(tokens.length);
    document.getElementById("id_adr_line_1").value = tokens[0];
    document.getElementById("id_adr_line_2").value = tokens[1];
    document.getElementById("id_adr_line_3").value = tokens[2];
    document.getElementById("id_adr_line_4").value = tokens[3];
    document.getElementById("id_locality").value = tokens[4];
    document.getElementById("id_city").value = tokens[5];
    document.getElementById("id_county").value = tokens[6];

}
function load_calendar() {
    console.log("load cal called")
    $(document).ready(function (){
        const elem = $("#availability-calendar");
        const url = elem.attr("data-ajax-url");
        const item_slug = elem.attr("data-item-slug");
        console.log(url)
        $.ajax({
            url : url,
            data : {'item_slug' : item_slug},
            success: function (){

            }

        });


    });

}

function subscribe_to_proposal(){
    console.log("you pressed subs button")
    // get the user - same way as in get user ajax function
    console.log("getting user")
        const full_data = $("#profile-link").attr("data-username-url");
        const btn = $("#subscribe-btn");
        const url = btn.attr("data-url-action");
        console.log("printing url of request");
        console.log(url);
        const elems = full_data.split('-');
        // console.log(elems[0], elems[1]);
        username = elems[1];
        const proposal_slug = btn.attr("data-prop-slug");
         $.ajax({
             //type : "POST",
             url : url,
             data : {'username': username, 'proposal_slug':proposal_slug },
             success : function(){
                 console.log(this);
                 if (btn.attr("value") === "Unsubscribe") {
                     btn.html("Subscribe");
                     btn.attr("value", "Subscribe");
                     btn.attr("data-url-action","/sharespace/ajax/sub_proposal/");
                 }else{
                     btn.html("Unsubscribe");
                     btn.attr("value", "Unsubscribe");
                     btn.attr("data-url-action","/sharespace/ajax/unsub_proposal/");
                 }

                 console.log("subs request complete");

            }
        });


}
