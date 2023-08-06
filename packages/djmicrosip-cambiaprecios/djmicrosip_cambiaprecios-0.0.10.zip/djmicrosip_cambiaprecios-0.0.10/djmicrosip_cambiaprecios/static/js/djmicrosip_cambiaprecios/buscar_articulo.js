function seleccionar_articulo(){
	location.href="/cambiaprecios/articulo/"+$(this).val();
}

$("#id_articulo").on("change",seleccionar_articulo);
