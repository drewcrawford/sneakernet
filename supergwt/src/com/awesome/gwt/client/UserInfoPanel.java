package com.awesome.gwt.client;

import java.util.HashMap;

import com.google.gwt.user.client.ui.VerticalPanel;
import com.google.gwt.user.client.ui.Label;

public class UserInfoPanel extends VerticalPanel {
	static UserInfoPanel singleInstance;
	public UserInfoPanel(String userInfoString)
	{
		reBuild(userInfoString);
		singleInstance = this;
	}
	public static void reBuild()
	{
		HashMap h = new HashMap();
		h.put("username", UserMgmt.username);
		h.put("password", UserMgmt.password);
		magic.sneakerpost(h, "/userinfo", new StringCallback() {

			@Override
			void doSomethingWithString(String s) {
				singleInstance.reBuild(s);
				
			}
			
		});
	}
	private void reBuild(String userInfoString) {
		this.clear();
		String[] lines = userInfoString.split("\n");
		String labelstr = UserMgmt.username + " | " + lines[1] + " points";
		this.add(new Label(labelstr));
		if (lines[3].startsWith("FREELEECH"))
		{
			this.add(new Label("Freeleech is on.  For now, all requests are free!"));
		}
		
		//this.add(new Label(lines[1] + " points"));
	}

}
