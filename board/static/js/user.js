function idCheck() {
    if (!$('#username').val()) 
    {
        alert("ID를 입력해 주시기 바랍니다.");
        return
    }

    $.ajax({
        type: "POST",
        url: "/boardapp/user_register_idcheck/",
        data: {
            'username': $('#username').val(),
            'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function(response){
            $('#idcheck-result').html(response);
        },
    });
}