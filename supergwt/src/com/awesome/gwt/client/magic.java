package com.awesome.gwt.client;
import java.util.Dictionary;

import com.google.gwt.dev.util.collect.HashMap;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.http.client.URL;
import com.google.gwt.user.client.Window;



public class magic {
	//Assumes the return info is a URL to a .sneak file
	static void sneakerpost(java.util.HashMap h, final String url)
	{
		magic.sneakerpost(h, url, new StringCallback() {

			@Override
			void doSomethingWithString(String s) {
				Window.open(s, "_self", "");
				
			}
			
		});
	}
	static void sneakerget(java.util.HashMap h, String url, final StringCallback callback)
	{
		StringBuilder sb = new StringBuilder();
		sb.append(url + "?");
		for(Object oparam: h.keySet())
		{
			String param = (String) oparam;
			sb.append(reallyEncode(param));
			sb.append("=");
			sb.append(reallyEncode((String) h.get(param)));
			sb.append("&");
		}
		RequestBuilder builder = new RequestBuilder(RequestBuilder.GET,sb.toString());
		try {
			builder.sendRequest(null, new RequestCallback() {

				@Override
				public void onError(Request request, Throwable exception) {
					Window.alert("Error #3");
					
				}

				@Override
				public void onResponseReceived(Request request,
						Response response) {
					callback.doSomethingWithString(response.getText());
					
				}
				
			});

		}
		catch(RequestException e)
		{
			Window.alert("Error #2");
		}
	}
	static String reallyEncode(String input)
	{
	String ret = URL.encode(input);
	ret = ret.replace("&", "%26");
	ret = ret.replace("$", "%24");
	ret = ret.replace("+", "%2B");
	ret = ret.replace(",", "%2C");
	ret = ret.replace("/", "%2F");
	ret = ret.replace(":", "%3A");
	ret = ret.replace("=", "%3D");
	ret = ret.replace("?", "%3F");
	//ret = ret.replace("@", "%64");
	return ret;
	}
	static void sneakerpost(java.util.HashMap h, String url, final StringCallback callback)
	{
		StringBuilder sb = new StringBuilder();
		//sb.append(url);
		for (Object oparam : h.keySet())
		{
			String param = (String) oparam;
			sb.append(reallyEncode(param));
			sb.append("=");
			sb.append(reallyEncode((String) h.get(param)));
			sb.append("&");
		}
		RequestBuilder builder = new RequestBuilder(RequestBuilder.POST,url);
		builder.setHeader("Content-type", "application/x-www-form-urlencoded");
		try {
			builder.sendRequest(sb.toString(), new RequestCallback() {

				@Override
				public void onError(Request request, Throwable exception) {
					// TODO Auto-generated method stub
					Window.alert("Error ocurred");
				}

				@Override
				public void onResponseReceived(Request request, Response response) {
					// TODO Auto-generated method stub
					callback.doSomethingWithString(response.getText());
				}
				
			});
		} catch (RequestException e) {
			// TODO Auto-generated catch block
			Window.alert("Error #1");
			e.printStackTrace();
		}
		
	}
}
