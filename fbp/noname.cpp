///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version Jun  6 2014)
// http://www.wxformbuilder.org/
//
// PLEASE DO "NOT" EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#include "noname.h"

///////////////////////////////////////////////////////////////////////////

MyFrame1::MyFrame1( wxWindow* parent, wxWindowID id, const wxString& title, const wxPoint& pos, const wxSize& size, long style ) : wxFrame( parent, id, title, pos, size, style )
{
	this->SetSizeHints( wxDefaultSize, wxDefaultSize );
	
	wxStaticBoxSizer* tabNodeSZ;
	tabNodeSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT(" State ") ), wxVERTICAL );
	
	wxGridSizer* tabNodeSZ1;
	tabNodeSZ1 = new wxGridSizer( 2, 3, 3, 3 );
	
	wxStaticBoxSizer* tabNodeValveSZ;
	tabNodeValveSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT("Valve") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeValveSZ1;
	tabNodeValveSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeValveBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/magnet.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeValveSZ1->Add( tabNodeValveBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeValveSZ2;
	tabNodeValveSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeValveL1 = new wxStaticText( this, wxID_ANY, wxT("Signal:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeValveL1->Wrap( -1 );
	tabNodeValveSZ2->Add( tabNodeValveL1, 0, wxALL, 5 );
	
	tabNodeValveL2 = new wxStaticText( this, wxID_ANY, wxT("OFF"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeValveL2->Wrap( -1 );
	tabNodeValveL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeValveSZ2->Add( tabNodeValveL2, 0, wxALL, 5 );
	
	
	tabNodeValveSZ1->Add( tabNodeValveSZ2, 0, wxEXPAND, 5 );
	
	wxBoxSizer* tabNodeValveSZ3;
	tabNodeValveSZ3 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeValveL3 = new wxStaticText( this, wxID_ANY, wxT("Signal received:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeValveL3->Wrap( -1 );
	tabNodeValveSZ3->Add( tabNodeValveL3, 0, wxALL, 5 );
	
	tabNodeValveL4 = new wxStaticText( this, wxID_ANY, wxT("OFF"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeValveL4->Wrap( -1 );
	tabNodeValveL4->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeValveSZ3->Add( tabNodeValveL4, 0, wxALL, 5 );
	
	
	tabNodeValveSZ1->Add( tabNodeValveSZ3, 0, wxEXPAND, 5 );
	
	
	tabNodeValveSZ->Add( tabNodeValveSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeValveSZ, 0, wxEXPAND, 5 );
	
	wxStaticBoxSizer* tabNodeBatSZ;
	tabNodeBatSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT("Battery") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeBatSZ1;
	tabNodeBatSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeBatBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/battery.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeBatSZ1->Add( tabNodeBatBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeBatSZ2;
	tabNodeBatSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeBatL1 = new wxStaticText( this, wxID_ANY, wxT("Voltage:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeBatL1->Wrap( -1 );
	tabNodeBatSZ2->Add( tabNodeBatL1, 0, wxALL, 5 );
	
	tabNodeBatL2 = new wxStaticText( this, wxID_ANY, wxT("0.00"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeBatL2->Wrap( -1 );
	tabNodeBatL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeBatSZ2->Add( tabNodeBatL2, 0, wxALL, 5 );
	
	tabNodeBatL3 = new wxStaticText( this, wxID_ANY, wxT("Vdc"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeBatL3->Wrap( -1 );
	tabNodeBatSZ2->Add( tabNodeBatL3, 0, wxALL, 5 );
	
	
	tabNodeBatSZ1->Add( tabNodeBatSZ2, 0, wxEXPAND, 5 );
	
	wxBoxSizer* tabNodeBatSZ3;
	tabNodeBatSZ3 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeBatG1 = new wxGauge( this, wxID_ANY, 100, wxDefaultPosition, wxDefaultSize, wxGA_HORIZONTAL );
	tabNodeBatG1->SetValue( 0 ); 
	tabNodeBatSZ3->Add( tabNodeBatG1, 1, wxALL, 5 );
	
	
	tabNodeBatSZ1->Add( tabNodeBatSZ3, 1, wxEXPAND, 5 );
	
	
	tabNodeBatSZ->Add( tabNodeBatSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeBatSZ, 0, wxEXPAND, 5 );
	
	wxStaticBoxSizer* tabNodeSolarSZ;
	tabNodeSolarSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT("Solar") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeSolarSZ1;
	tabNodeSolarSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeSolarBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/solar.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeSolarSZ1->Add( tabNodeSolarBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeSolarSZ2;
	tabNodeSolarSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeSolarL1 = new wxStaticText( this, wxID_ANY, wxT("Voltage:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeSolarL1->Wrap( -1 );
	tabNodeSolarSZ2->Add( tabNodeSolarL1, 0, wxALL, 5 );
	
	tabNodeSolarL2 = new wxStaticText( this, wxID_ANY, wxT("0.00"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeSolarL2->Wrap( -1 );
	tabNodeSolarL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeSolarSZ2->Add( tabNodeSolarL2, 0, wxALL, 5 );
	
	tabNodeSolarL2 = new wxStaticText( this, wxID_ANY, wxT("Vdc"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeSolarL2->Wrap( -1 );
	tabNodeSolarSZ2->Add( tabNodeSolarL2, 0, wxALL, 5 );
	
	
	tabNodeSolarSZ1->Add( tabNodeSolarSZ2, 0, wxEXPAND, 5 );
	
	wxBoxSizer* tabNodeSolarSZ3;
	tabNodeSolarSZ3 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeSolarG1 = new wxGauge( this, wxID_ANY, 100, wxDefaultPosition, wxDefaultSize, wxGA_HORIZONTAL );
	tabNodeSolarG1->SetValue( 0 ); 
	tabNodeSolarSZ3->Add( tabNodeSolarG1, 1, wxALL, 5 );
	
	
	tabNodeSolarSZ1->Add( tabNodeSolarSZ3, 1, wxEXPAND, 5 );
	
	
	tabNodeSolarSZ->Add( tabNodeSolarSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeSolarSZ, 0, wxEXPAND, 5 );
	
	wxStaticBoxSizer* tabNodeLedSZ;
	tabNodeLedSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT("LED") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeLedSZ1;
	tabNodeLedSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeLedBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/led.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeLedSZ1->Add( tabNodeLedBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeLedSZ2;
	tabNodeLedSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeLedL1 = new wxStaticText( this, wxID_ANY, wxT("State:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeLedL1->Wrap( -1 );
	tabNodeLedSZ2->Add( tabNodeLedL1, 0, wxALL, 5 );
	
	tabNodeLedL2 = new wxStaticText( this, wxID_ANY, wxT("OFF"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeLedL2->Wrap( -1 );
	tabNodeLedL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeLedSZ2->Add( tabNodeLedL2, 0, wxALL, 5 );
	
	
	tabNodeLedSZ1->Add( tabNodeLedSZ2, 0, wxEXPAND, 5 );
	
	
	tabNodeLedSZ->Add( tabNodeLedSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeLedSZ, 1, wxEXPAND, 5 );
	
	wxStaticBoxSizer* tabNodeShockSZ;
	tabNodeShockSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT("Shock sensor") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeShockSZ1;
	tabNodeShockSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeShockBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/tornado.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeShockSZ1->Add( tabNodeShockBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeShockSZ2;
	tabNodeShockSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeShockL1 = new wxStaticText( this, wxID_ANY, wxT("State:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeShockL1->Wrap( -1 );
	tabNodeShockSZ2->Add( tabNodeShockL1, 0, wxALL, 5 );
	
	tabNodeShockL2 = new wxStaticText( this, wxID_ANY, wxT("OFF"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeShockL2->Wrap( -1 );
	tabNodeShockL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeShockSZ2->Add( tabNodeShockL2, 0, wxALL, 5 );
	
	
	tabNodeShockSZ1->Add( tabNodeShockSZ2, 1, wxEXPAND, 5 );
	
	
	tabNodeShockSZ->Add( tabNodeShockSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeShockSZ, 1, wxEXPAND, 5 );
	
	wxStaticBoxSizer* tabNodeInfoSZ;
	tabNodeInfoSZ = new wxStaticBoxSizer( new wxStaticBox( this, wxID_ANY, wxT(" Info ") ), wxVERTICAL );
	
	wxBoxSizer* tabNodeInfoSZ1;
	tabNodeInfoSZ1 = new wxBoxSizer( wxVERTICAL );
	
	tabNodeInfoBmp = new wxStaticBitmap( this, wxID_ANY, wxBitmap( wxT("../images/information.png"), wxBITMAP_TYPE_ANY ), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoSZ1->Add( tabNodeInfoBmp, 0, wxALL, 5 );
	
	wxBoxSizer* tabNodeInfoSZ2;
	tabNodeInfoSZ2 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeInfoL1 = new wxStaticText( this, wxID_ANY, wxT("Version:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL1->Wrap( -1 );
	tabNodeInfoSZ2->Add( tabNodeInfoL1, 0, wxALL, 5 );
	
	tabNodeInfoL2 = new wxStaticText( this, wxID_ANY, wxT("1.0"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL2->Wrap( -1 );
	tabNodeInfoL2->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeInfoSZ2->Add( tabNodeInfoL2, 0, wxALL, 5 );
	
	
	tabNodeInfoSZ1->Add( tabNodeInfoSZ2, 1, wxEXPAND, 5 );
	
	wxBoxSizer* tabNodeInfoSZ3;
	tabNodeInfoSZ3 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeInfoL3 = new wxStaticText( this, wxID_ANY, wxT("HW:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL3->Wrap( -1 );
	tabNodeInfoSZ3->Add( tabNodeInfoL3, 0, wxALL, 5 );
	
	tabNodeInfoL4 = new wxStaticText( this, wxID_ANY, wxT("XXXXXX"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL4->Wrap( -1 );
	tabNodeInfoL4->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeInfoSZ3->Add( tabNodeInfoL4, 0, wxALL, 5 );
	
	
	tabNodeInfoSZ1->Add( tabNodeInfoSZ3, 1, wxEXPAND, 5 );
	
	wxBoxSizer* tabNodeInfoSZ4;
	tabNodeInfoSZ4 = new wxBoxSizer( wxHORIZONTAL );
	
	tabNodeInfoL5 = new wxStaticText( this, wxID_ANY, wxT("SW:"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL5->Wrap( -1 );
	tabNodeInfoSZ4->Add( tabNodeInfoL5, 0, wxALL, 5 );
	
	tabNodeInfoL6 = new wxStaticText( this, wxID_ANY, wxT("XXXXXX"), wxDefaultPosition, wxDefaultSize, 0 );
	tabNodeInfoL6->Wrap( -1 );
	tabNodeInfoL6->SetFont( wxFont( 10, 74, 90, 92, false, wxT("Sans") ) );
	
	tabNodeInfoSZ4->Add( tabNodeInfoL6, 0, wxALL, 5 );
	
	
	tabNodeInfoSZ1->Add( tabNodeInfoSZ4, 1, wxEXPAND, 5 );
	
	
	tabNodeInfoSZ->Add( tabNodeInfoSZ1, 0, wxEXPAND, 5 );
	
	
	tabNodeSZ1->Add( tabNodeInfoSZ, 1, wxEXPAND, 5 );
	
	
	tabNodeSZ->Add( tabNodeSZ1, 1, wxEXPAND, 1 );
	
	
	this->SetSizer( tabNodeSZ );
	this->Layout();
	
	this->Centre( wxBOTH );
}

MyFrame1::~MyFrame1()
{
}
