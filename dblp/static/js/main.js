$(document).ready(function(){
    $('#submit_query').attr('disabled',true);
    $('#queryInput').keyup(function(){
        if($(this).val().length !=0)
            $('#submit_query').attr('disabled', false);            
        else
            $('#submit_query').attr('disabled',true);
    })
});