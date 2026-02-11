import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FichierScannerComponent } from './fichier-scanner.component';

describe('FichierScannerComponent', () => {
  let component: FichierScannerComponent;
  let fixture: ComponentFixture<FichierScannerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FichierScannerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FichierScannerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
