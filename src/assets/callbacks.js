if (!window.dash_clientside) {
    window.dash_clientside = {}
}


window.dash_clientside.clientside1 = {
    update_graph: function(model, term, surf, display) {
	/**
	 * Update the first brain map
	 *
	 * Parameters
	 * ----------
	 *
	 * model: str
	 *     folder containing results of 1 model
	 * term: str
	 *     term in the model
	 * surf: str
	 *    flat, infl, pial, sphere
	 * display: str
	 *     view='lateral'
	 */
	 var clust, new_surf;

	 clust = display === "Betas" ? false : true;

	 new_surf = plot_surfmap({
        "model": model,
        "term": term,
        "surf": surf,
        "show_clusters": clust
     })[0];

     return [new_surf["left"].figure, new_surf["right"].figure];
};