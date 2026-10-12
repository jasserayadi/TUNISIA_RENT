import { Directive, ElementRef, Input, OnDestroy, OnInit, inject } from '@angular/core';

@Directive({
  selector: '[appReveal]',
  standalone: true
})
export class RevealDirective implements OnInit, OnDestroy {
  @Input() revealDelay = 0;
  @Input() revealY = 30;

  private el = inject(ElementRef<HTMLElement>);
  private observer?: IntersectionObserver;

  ngOnInit(): void {
    const node = this.el.nativeElement;
    node.style.opacity = '0';
    node.style.transform = `translateY(${this.revealY}px)`;
    node.style.transition =
      `opacity 700ms cubic-bezier(.2,.8,.2,1) ${this.revealDelay}ms, ` +
      `transform 700ms cubic-bezier(.2,.8,.2,1) ${this.revealDelay}ms`;

    if (typeof IntersectionObserver === 'undefined') {
      node.style.opacity = '1';
      node.style.transform = 'none';
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            node.style.opacity = '1';
            node.style.transform = 'translateY(0)';
            this.observer?.unobserve(node);
          }
        });
      },
      { threshold: 0.12 }
    );
    this.observer.observe(node);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }
}