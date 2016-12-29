$("#pesf_select").change(function() {
    var pesf_id = $(this).find(":selected").val();
    /*$('#res_cap').val(pesf_id);*/

    /*get values from select field*/
    var val = $.map($('#pesf_select option'),
                       function(e) { return e.text; });


    $('#sesf_select').empty();
    /* populate select field with removing selected field*/
    $.each(val,function(e){
        if (e!=pesf_id && e!=0)
          $('#sesf_select').append('<option value="">' + val[e] + '</option>');
    });


});

$(document).ready(function() {
   $("#addToList").click(function() {

            var new_cap = $.trim($("#add_cap").val());

            var dest = $("#res_cap");
            if (new_cap && dest.val())
            dest.val(dest.val()+'\n'+new_cap);
            else
                dest.val(new_cap);
            $("#add_cap").val('');



});
 $( function() {
    $( "this #start-date" ).datepicker();
  } );
});



  var requestsProcessing = function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var resourceid = button.data('resourceid') // Extract info from data-* attributes
  var incidentid = button.data('incidentid')
  var action=button.data('action')
  var modal = $(this)
  modal.find('.modal-title').text(action+' Resource  with ResourceID:'+resourceid+' and IncidentID: ' + incidentid)

     $( function() {
    $( "this #start-date" ).datepicker("show");
  } );

  $('input[id=incident-id]').val(incidentid)
  $('input[id=resource-id]').val(resourceid)
};

  var repairsProcessing =  function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var resourceid = button.data('resourceid') // Extract info from data-* attributes
  var incidentid = button.data('incidentid')
  var nextdate = button.data('nextdate')
  var modal = $(this)
  modal.find('.modal-title').text('Repair Resource starting '+ nextdate)

  $('input[id=r-incident-id]').val(incidentid)
  $('input[id=r-resource-id]').val(resourceid)

  $('input[id=r-start-date]').val(nextdate)

}

$('#RepairModal').on('show.bs.modal', repairsProcessing);
$('#CancelRepairModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var resourceid = button.data('resourceid') // Extract info from data-* attributes
  var repairid = button.data('repairid')
  console.log(repairid)
  var modal = $(this)
  modal.find('.modal-title').text('Cancel Repair for Resource'+ resourceid)

  $('input[id=cr-resource-id]').val(resourceid)
  $('input[id=cr-repair-id]').val(repairid)
})

  $('#DeployModal').on('show.bs.modal', requestsProcessing);
  $('#ReturnModal').on('show.bs.modal', requestsProcessing);
  $('#RejectModal').on('show.bs.modal', requestsProcessing);
  $('#CancelRequestModal').on('show.bs.modal', requestsProcessing);
  $('#RequestModal').on('show.bs.modal', requestsProcessing);



$('#RequestModal button.btn.btn-primary').click(function(event)
    {

    console.log($('#myrequest').serialize());
    $.post('/request_resource/', $('#myrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#RequestModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })
    });


$('#RepairModal button.btn.btn-primary').click(function(event)
    {
        console.log($('#repairrequest'))
    $.post('/repair_resource/', $('#repairrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#RepairModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });


$('#DeployModal button.btn.btn-primary').click(function(event)
    {

    $.post('/deploy_resource/', $('#deployrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#DeployModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });

$('#ReturnModal button.btn.btn-primary').click(function(event)
    {

    $.post('/return_request/', $('#returnrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#ReturnModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });

$('#CancelRequestModal button.btn.btn-primary').click(function(event)
    {

    $.post('/cancel_request/', $('#cancelrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#CancelRequestModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });

   $('#CancelRepairModal button.btn.btn-primary').click(function(event)
    {

    $.post('/cancel_repair/', $('#cancelrepair').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#CancelRepairModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });

$('#RejectModal button.btn.btn-primary').click(function(event)
    {

    $.post('/reject_request/', $('#rejectrequest').serialize(), function(data, status, xhr)
        {
        // do something here with response;
            console.info(data);
            console.info(status);
            console.info(xhr);
        })
        .done(function() {
        // do something here if done ;
           alert( "Success!" );
           $("#RejectModal").modal('hide');

        })
        .fail(function() {
        // do something here if there is an error ;
            alert( "error" );
        })

    });
