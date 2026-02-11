import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateSemestreComponent } from './update-semestre.component';

describe('UpdateSemestreComponent', () => {
  let component: UpdateSemestreComponent;
  let fixture: ComponentFixture<UpdateSemestreComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UpdateSemestreComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UpdateSemestreComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
