package com.awesome.gwt.client;

import java.util.HashMap;

import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.VerticalPanel;

public class ResultsPanel extends VerticalPanel  {
	void reBuildPanel(String queryURL)
	{
		this.clear();
		final ResultsPanel thi = this;
		magic.sneakerget(new HashMap(), queryURL, new StringCallback() {

			@Override
			void doSomethingWithString(String s) {
				if (s=="")
				{
					thi.add(new Label("I've got nothing for you..."));
				}
				else
				{
					for (String items:  s.split("\n"))
					{
						Result r = new Result(items);
						thi.add(r);
					}
				}
				
			}
			
		});
	}
}
