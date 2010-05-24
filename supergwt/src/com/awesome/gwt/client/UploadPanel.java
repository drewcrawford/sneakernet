package com.awesome.gwt.client;

import java.util.HashMap;
import java.util.Iterator;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.*;

public class UploadPanel extends VerticalPanel {

	VerticalPanel specific;
public UploadPanel()
{
	super();
	HTMLPanel rules = new HTMLPanel("<font color='red'>STOP!  HAVE YOU READ THE RULES?</font>");
	this.add(rules);
	this.add(new Label("Sharing files with sneakernet is a great way to improve your score."));
	HorizontalPanel choose = new HorizontalPanel();
	RadioButton b_movie = new RadioButton("upload","movie");
	RadioButton b_software = new RadioButton("upload","software");
	RadioButton b_book = new RadioButton("upload","book");
	b_book.addClickHandler(new ClickHandler() {

		@Override
		public void onClick(ClickEvent event) {
			specific.clear();
			Label t = new Label("Title");
			final TextBox title = new TextBox();
			Label i = new Label("Amazon link");
			final TextBox amzn = new TextBox();
			specific.add(t);
			specific.add(title);
			specific.add(i);
			specific.add(amzn);
			
			Button upload = new Button("Share");
			specific.add(upload);
			upload.addClickHandler(new ClickHandler() {

				@Override
				public void onClick(ClickEvent event) {
					HashMap h = new HashMap();
					h.put("username",UserMgmt.username);
					h.put("password", UserMgmt.password);
					h.put("title", title.getText());
					h.put("amzn", amzn.getText());
					magic.sneakerpost(h,"/share/book");
					
				}
				
			});
			
		}
		
	});
	b_movie.addClickHandler(new ClickHandler() 
	{

		@Override
		public void onClick(ClickEvent event) {
		//	Window.alert("Hey!");
			specific.clear();
			Label t= new Label("Title");
			final TextBox title = new TextBox();
			
			Label i = new Label("IMDB Link (go find it on imdb.com)");
			final TextBox imdb = new TextBox();
			specific.add(t);
			specific.add(title);
			specific.add(i);
			specific.add(imdb);
			
			Button upload = new Button("Share");
			specific.add(upload);
			
			upload.addClickHandler(new ClickHandler() {

				@Override
				public void onClick(ClickEvent event) {
					// TODO Auto-generated method stub
					HashMap h = new HashMap();
					h.put("title", title.getText());
					h.put("imdb", imdb.getText());
					h.put("username", UserMgmt.username);
					h.put("password", UserMgmt.password);
					magic.sneakerpost(h, "/share/movie");
					
				}
				
			});
			
			
			
			
		}
	});
	choose.add(b_movie);
	choose.add(b_software);
	choose.add(b_book);
	this.add(choose);
	specific = new VerticalPanel();
	this.add(specific);
	
	
}

}
