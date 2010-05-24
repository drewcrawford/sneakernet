package com.awesome.gwt.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.core.client.GWT;
import com.google.gwt.dev.util.collect.HashMap;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.event.dom.client.KeyUpEvent;
import com.google.gwt.event.dom.client.KeyUpHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.*;

/**
 * Entry point classes define <code>onModuleLoad()</code>.
 */
public class Supergwt implements EntryPoint {
	Hyperlink signin = new Hyperlink();
	TabPanel t = new TabPanel();
	final DockPanel d = new DockPanel();
	SearchPanel search = new SearchPanel();
	public void onModuleLoad() {
		RootPanel.get().add(d);
		signin.setText("Sign in");
		signin.addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				showLogin();
				
			}
		});
		showLogin();
		
		

		
		
		d.add(signin,DockPanel.EAST);
		d.add(t,DockPanel.CENTER);
		

		t.add(search,"Home");
		
		t.add(new Rules(),"Rules");
		d.add(new com.google.gwt.user.client.ui.Label("This is so much cooler than you'd expect."),DockPanel.SOUTH);
		d.add(new HTMLPanel("Don't know how to open a .sneak file?  Click <a href=\"/install\">here</a>"),DockPanel.SOUTH);
		
		t.selectTab(0);
		
	}
		
		
		
		private void showLogin() {
			final DialogBox diag = new DialogBox();
			VerticalPanel v = new VerticalPanel();
			diag.add(v);
			Label u = new Label("username");
			final TextBox username = new TextBox();
			v.add(u);
			v.add(username);

			
			Label p = new Label("password");
			final PasswordTextBox password = new PasswordTextBox();

			v.add(p);
			v.add(password);
			
			final Button Login = new Button("login");
			v.add(Login);
			
			password.addKeyPressHandler(new KeyPressHandler() {

				@Override
				public void onKeyPress(KeyPressEvent event) {
					if (event.getCharCode()==13)
					{
						Login.click();
					}
					
				}
				
			});
			Hyperlink l = new Hyperlink();
			l.setText("I don't want to log in...");
			l.addClickHandler(new ClickHandler() {

				@Override
				public void onClick(ClickEvent event) {
					diag.hide();
					
				}
				
			});
			v.add(l);
			diag.center();
			username.setFocus(true);
			
			Login.addClickHandler(new ClickHandler() {

				@Override
				public void onClick(ClickEvent event) {
					java.util.HashMap h = new java.util.HashMap();
					h.put("username", username.getText());
					h.put("password",password.getText());
					
					magic.sneakerpost(h, "/userinfo", new StringCallback() {

						@Override
						void doSomethingWithString(String s) {
							if (s.startsWith("SUCCESS"))
							{
								signin.removeFromParent();
								UploadPanel up = new UploadPanel();
								t.add(up,"Upload");
								diag.hide();
								UserMgmt.username = username.getText();
								UserMgmt.password = password.getText();
								UserInfoPanel pan = new UserInfoPanel(s);
								d.add(pan,DockPanel.EAST);
								String[] items = s.split("\n");
								if (items[2]=="TEAM_LEADER")
								{
									TeamLeaderPanel tp = new TeamLeaderPanel();
									t.add(tp,"Team Leader");
								}
								
							}
							
						}
						
					});
					
				}
				
			});
		}
		
}
