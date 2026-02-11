import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReponseetudiantComponent } from './reponseetudiant.component';

describe('ReponseetudiantComponent', () => {
  let component: ReponseetudiantComponent;
  let fixture: ComponentFixture<ReponseetudiantComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReponseetudiantComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReponseetudiantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
