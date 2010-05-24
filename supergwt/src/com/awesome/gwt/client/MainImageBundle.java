package com.awesome.gwt.client;
import com.google.gwt.user.*;
import com.google.gwt.user.client.ui.AbstractImagePrototype;
import com.google.gwt.user.client.ui.ImageBundle;

public interface MainImageBundle extends ImageBundle{

	@Resource("down_16.png")
	public AbstractImagePrototype download_icon();
}
