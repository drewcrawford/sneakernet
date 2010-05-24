//
//  macportAppDelegate.m
//  macport
//
//  Created by Drew Crawford on 12/15/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "macportAppDelegate.h"

@implementation macportAppDelegate

@synthesize window;

-(BOOL) application:(NSApplication*) theApplication
		   openFile:(NSString*) file
{
	NSLog(@"Sneakernet is going to launch something...");
	NSString *source = [NSString stringWithFormat:@"tell application \"Terminal\"\ndo script \"python %@ %@\"\nend tell",[[NSBundle mainBundle] pathForResource:@"sneak" ofType:@"pyo"], file];
	 NSAppleScript *script = [[NSAppleScript alloc] initWithSource:source];
	NSDictionary *scriptError = [[NSDictionary alloc] init];
	[script executeAndReturnError:&scriptError];
	[[NSApplication sharedApplication] terminate:self];
	//[script exe

}
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
	// Insert code here to initialize your application 
}


@end
