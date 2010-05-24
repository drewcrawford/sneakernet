package com.awesome.gwt.client;

import java.util.HashMap;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.*;

public class TeamLeaderPanel extends VerticalPanel {
	
	public void  add_cache_backend(String cache_info_str)
	{
		//[0] = type
		//[1] = description
		//[2] = imageurl
		//[3] = key
		//[4] = flashdiskinfos (comma-seperated)
		String[] args = "".split("\n");
		if (cache_info_str!=null) args = cache_info_str.split(";");
		final FormPanel f = new FormPanel();
		this.add(f);
		f.setAction("/teamadmin/cacheinfo");
		f.setEncoding(FormPanel.ENCODING_MULTIPART);
		f.setMethod(FormPanel.METHOD_POST);
		
		VerticalPanel inside = new VerticalPanel();
		f.setWidget(inside);
		ListBox lb = new ListBox();
		lb.setName("cache-type");
		lb.addItem("Internal (team-only) cache","INTERN");
		lb.addItem("External cache","EXTERN");
		
		if (cache_info_str != null)
		{
			//since there are only two types, we only need to alter the selection if it's EXTERN
			if (args[0]=="EXTERN")
				lb.setItemSelected(1, true);
		}
		inside.add(lb);
		Label d = new Label("Cache description:  Please provide all the information necessary to find and locate the cache.");
		inside.add(d);
		TextArea desc = new TextArea();
		desc.setHeight("500 px");
		desc.setWidth("500 px");
		desc.setName("description");
		if (cache_info_str != null)
		{
			desc.setText(args[1]);
		}
		inside.add(desc);
		if (cache_info_str != null)
		{
			Image i = new Image(args[2]);
			inside.add(i);
		}
		d = new Label("Replace the photo of this cache (max size: 1MB)");
		inside.add(d);
		FileUpload u = new FileUpload();
		u.setName("image");
		//hidden stuff
		TextBox hidden = new TextBox();
		hidden.setVisible(false);
		hidden.setName("username");
		hidden.setText(UserMgmt.username);
		inside.add(hidden);
		hidden = new TextBox();
		hidden.setVisible(false);
		hidden.setName("password");
		hidden.setText(UserMgmt.password);
		inside.add(hidden);
		hidden = new TextBox();
		hidden.setVisible(false);
		hidden.setName("cache-key");
		if (cache_info_str==null)
		{
			hidden.setText("MAKENEW");
		}
		else
		{
			hidden.setText(args[3]);
		}
		inside.add(hidden);
		inside.add(u);
		
		inside.add(new Button(cache_info_str==null?"Add new cache":"Edit cache",new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				f.submit();
				Window.alert("Your changes were probably saved; however you must refresh to see them...");
				
			}
			
		}));
		if (cache_info_str!=null)
		{
			this.add(new Label("The cache has the following flash disks inside:"));
			String[] disks = args[4].split(",");
			for (String disk : disks)
			{
				this.add(new Label(disk));
			}
		}
	}
	public TeamLeaderPanel()
	{
		final TeamLeaderPanel thi = this;
		final HashMap h = new HashMap();
		h.put("username", UserMgmt.username);
		h.put("password", UserMgmt.password);
		
		magic.sneakerget(h, "/teamadmin/cacheinfo", new StringCallback() {

			@Override
			void doSomethingWithString(String s) {
				for (String line : s.split("\n"))
				{
					add_cache_backend(line);
				}
				
				
				//at the very end
				thi.add(new Label("Make a new cache, where none has existed before!"));
				thi.add_cache_backend(null);
				//invites
				magic.sneakerget(h, "/teamadmin/invite", new StringCallback() {

					@Override
					void doSomethingWithString(String s) {
						if (!s.startsWith("0"))
						{
							thi.add(new Label("You can invite more people to your team.  E-mail:"));
							final TextBox emailInvite = new TextBox();
							thi.add(emailInvite);
							Button b = new Button("Send Invite");
							thi.add(b);
							b.addClickHandler(new ClickHandler() {

								@Override
								public void onClick(ClickEvent event) {
									HashMap inviteMap = new HashMap();
									h.put("username", UserMgmt.username);
									h.put("password", UserMgmt.password);
									h.put("email", emailInvite.getText());
									magic.sneakerpost(h, "/teamadmin/invite");
									Window.alert("Your invite was probably sent...");
									
								}
								
							});
						}
						
					}
					
				});
			}
			
		});
		
		
		
		
	}
}
