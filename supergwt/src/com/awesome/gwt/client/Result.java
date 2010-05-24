package com.awesome.gwt.client;

import java.util.HashMap;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.*;

public class Result extends FlexTable {
	public Result(String resultStr)
	{
		String[] items = resultStr.split("~");
		Label type = new Label();
		if (items[1]=="0")
			type.setText("M");
		if (items[1]=="1")
			type.setText("B");
		this.setWidget(0, 0, type);
		HTMLPanel l = new HTMLPanel("<a href=\""+items[5]+"\">" + items[0] + "</a>");
		//Hyperlink l = new Hyperlink(items[0],items[1]);

		this.setWidget(0, 1, l);
		long size = Long.parseLong(items[3]);
		Label lsize = new Label();
		lsize.setText(size/1024/1024 + "MB");
		this.setWidget(0, 2, lsize);
		MainImageBundle mib = GWT.create(MainImageBundle.class);
		Image download_icon = mib.download_icon().createImage();
		this.setWidget(0,3,download_icon);
		final String key = items[4];
		download_icon.addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				if (UserMgmt.username== null)
				{
					Window.alert("You must be logged in.");
					return;
				}
				HashMap h = new HashMap();
				h.put("username", UserMgmt.username);
				h.put("password", UserMgmt.password);
				h.put("content", key);
				magic.sneakerpost(h, "/requests", new StringCallback() {

					@Override
					void doSomethingWithString(String s) {
						if (s.startsWith("NEEDMOREPOINTS "))
						{
							Window.alert("You don't have enough points.  You need " + s.substring(15) + " more points.");
						}
						else if (s.startsWith("OK"))
						{
							UserInfoPanel.reBuild();
							Window.alert("Sneakernet is now routing your files to you.");
							
						}
						
					}
					
				});
				
			}
			
		});
		
	}
}
