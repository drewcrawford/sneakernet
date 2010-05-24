package com.awesome.gwt.client;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.ui.*;

public class SearchPanel extends VerticalPanel {
	public SearchPanel()
	{
		final TextBox search = new TextBox();
		final ResultsPanel rp = new ResultsPanel();
		rp.reBuildPanel("/search/recent");
		search.setText("Type your search terms here to search...");
		search.setWidth("300 px");
		this.add(search);
		this.add(rp);
		search.addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				search.setText("");
				
			}
			
		});
		search.addKeyPressHandler(new KeyPressHandler() {

			@Override
			public void onKeyPress(KeyPressEvent event) {
				if (event.getCharCode()==13)
				{
					rp.reBuildPanel("/search/search?query="+URL.encode(search.getText()));
				}
				
			}
			
		});
	}
}
