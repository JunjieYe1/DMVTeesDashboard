// use a global for the submit and return data rendering in the examples



$(document).ready(function() {
var editor = new $.fn.dataTable.Editor( {

		table: '#Orders',
		fields: [
			{
				"label": "ID",
				"name": "orderid",
				"type": "int",
			},
			{
				"label": "OrderDate:",
				"name": "orderdate",
				"type": "datetime",
				"format": "ddd, D MMM YY"
			},
			{
				"label": "DueDate:",
				"name": "duedate",
				"type": "datetime",
				"format": "ddd, D MMM YY"
			},
			{
				"label": "Total:",
				"name": "total"
			},
			{
				"label": "OrderType:",
				"name": "ordertype",
				"type": "select",
				"options": [
					"Painting",
					"Drying",

				]
			},
			{
				"label": "Status:",
				"name": "status",
				"type": "select",
				"options": [
					"Pending",
					" Process",
					" Completed"
				]
			},
			{
				"label": "Emp:",
				"name": "emp",
				"type": "select",
				"options": [
					"1",
					"2",
					"3",
					"4",
					"5"
				]
			},
			{
				"label": "Customer:",
				"name": "customer"
			},
			{
				"label": "Design:",
				"name": "design"
			},
			{
				"label": "Item:",
				"name": "item"
			}
		]
	} );


    let data = [
           1,	'2020-03-03',	'2020-03-07',	2,	'Printing',	'Pending',	1,	1,	1	,1
        ];
    var table = $('#Orders').DataTable({
        data: data,
        order: [[1, 'asc']],
        columns: [
            {
                data: "id"

            },
            {
                data: "orderdate"
            },
            {
                data: "duedate"
            },
            {
                data: "total"
            },
            {
                data: "ordertype"
            },
            {
                data: "status"
            },
            {
                data: "emp"
            },
            {
                data: "customer"
            },
            {
                data: "design"
            },
            {
                data: "item"
            }
        ],
        select: true,
        lengthChange: false
    });


} );

