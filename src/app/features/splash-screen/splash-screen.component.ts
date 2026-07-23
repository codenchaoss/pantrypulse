import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { gsap } from 'gsap';

@Component({
  selector: 'app-splash-screen',
  templateUrl: './splash-screen.component.html',
  styleUrls: ['./splash-screen.component.scss']
})
export class SplashScreenComponent implements AfterViewInit {
  @ViewChild('splashContainer') splashContainer!: ElementRef;
  @ViewChild('energyBlast') energyBlast!: ElementRef;

  currentStyle = 'gold'; // Default style: gold, neon, or elastic

  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {
    // Read style query parameter, default to 'gold'
    this.route.queryParams.subscribe(params => {
      const styleParam = params['style'];
      if (styleParam && ['gold', 'neon', 'elastic'].includes(styleParam)) {
        this.currentStyle = styleParam;
      }
    });
  }

  ngAfterViewInit(): void {
    // Small timeout to ensure DOM is fully rendered
    setTimeout(() => {
      this.playStartupAnimation(this.currentStyle);
    }, 100);
  }

  private playStartupAnimation(style: string): void {
    const tl = gsap.timeline({
      onComplete: () => this.navigateToApp()
    });

    // Apply manual draw effect setup (stroke-dasharray) since we don't assume DrawSVG plugin
    const drawElements = document.querySelectorAll('.draw-path');
    drawElements.forEach((el: any) => {
      if (el.getTotalLength) {
        const length = el.getTotalLength();
        gsap.set(el, { strokeDasharray: length, strokeDashoffset: length });
      }
    });

    // Initial State Setup
    gsap.set('.logo-svg', { opacity: 1 });
    gsap.set(['#jar-1', '#jar-2', '#jar-3'], { y: -60, opacity: 0 });
    gsap.set('#bowl', { y: 30, opacity: 0 });
    gsap.set(['#leaf-small', '#leaf-big', '#text-leaf'], { scale: 0, transformOrigin: 'bottom center' });
    gsap.set('#cloche-handle', { scale: 0, transformOrigin: 'center' });
    gsap.set('#ecg-dot', { scale: 0, transformOrigin: 'center' });
    gsap.set(['#text-pantry', '#text-pulse'], { opacity: 0, x: 0 });
    gsap.set('#cutlery', { scale: 0.4, opacity: 0, transformOrigin: 'center center' });

    // Floating particles in the background
    const particles = document.querySelectorAll('.particle');
    particles.forEach((p) => {
      gsap.set(p, {
        x: 'random(0, 100vw)',
        y: 'random(0, 100vh)',
        scale: 'random(0.5, 1.5)'
      });
      gsap.to(p, {
        y: '-=100',
        x: 'random(-50, 50)',
        opacity: 'random(0.3, 0.8)',
        duration: style === 'neon' ? 'random(1, 2.5)' : 'random(2.5, 5)',
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    });

    const tagline = "SMART PANTRY. ZERO WASTE. MAX PROFIT.";

    if (style === 'neon') {
      // 1. NEON Tech Theme - Coordinated Simultaneous Assembly
      tl.to('#shelf path', { strokeDashoffset: 0, duration: 0.25, ease: 'power2.out', stagger: 0 })
        .to(['#jar-1', '#jar-2', '#jar-3'], { y: 0, opacity: 1, duration: 0.25, ease: 'power2.out', stagger: 0 }, '-=0.2')
        .to('#bowl', { y: 0, opacity: 1, duration: 0.25, ease: 'power2.out' }, '-=0.2')
        .to(['#leaf-big', '#leaf-small'], { scale: 1, duration: 0.2, ease: 'power2.out', stagger: 0 }, '-=0.15')
        
        .to('#cloche-arc', { strokeDashoffset: 0, duration: 0.25, ease: 'power3.out' }, '-=0.2')
        .to('#cloche-handle', { scale: 1, opacity: 1, duration: 0.15, ease: 'power3.out' }, '-=0.15')
        .to('#ecg-base', { strokeDashoffset: 0, duration: 0.15, ease: 'power2.out' }, '-=0.2')
        .to('#ecg-line', { strokeDashoffset: 0, duration: 0.3, ease: 'power4.out' }, '-=0.2')
        .to('#ecg-dot', { scale: 1, opacity: 1, duration: 0.15 }, '-=0.15')
        
        .to('.steam-path', { strokeDashoffset: 0, duration: 0.25, ease: 'power1.inOut', stagger: 0 }, '-=0.15')
        
        .to(['#text-pantry', '#text-pulse'], { opacity: 1, duration: 0.2 }, '-=0.15')
        .to('#text-leaf', { scale: 1, duration: 0.15 }, '-=0.1')
        
        .to('#tagline-lines', { strokeDashoffset: 0, duration: 0.15 }, '-=0.1');

      const typingObj = { val: 0 };
      tl.to(typingObj, {
        val: tagline.length,
        duration: 0.6,
        ease: 'none',
        onUpdate: () => {
          const charCount = Math.floor(typingObj.val);
          const tag1 = document.getElementById('tag-1');
          if (tag1) tag1.innerHTML = tagline.substring(0, charCount);
        }
      }, '-=0.15');

      tl.to('#cutlery', { scale: 0.6, opacity: 1, duration: 0.2, ease: 'power2.out' }, '-=0.15')
        .to('.logo-svg', { filter: 'drop-shadow(0 0 25px #00ffff) drop-shadow(0 0 35px #ff00ff)', duration: 0.3 });

      tl.to(this.energyBlast.nativeElement, {
        width: '300vw',
        height: '300vw',
        opacity: 1,
        duration: 0.6,
        ease: 'power4.in'
      }, '+=0.05')
      .to('.splash-container', { opacity: 0, duration: 0.2 }, '-=0.1');

    } else if (style === 'elastic') {
      // 2. ELASTIC Theme - Coordinated Spring Assembly
      tl.to('#shelf path', { strokeDashoffset: 0, duration: 0.45, ease: 'back.out(1.5)', stagger: 0 })
        .to(['#jar-1', '#jar-2', '#jar-3'], { y: 0, opacity: 1, duration: 0.5, ease: 'elastic.out(1, 0.45)', stagger: 0 }, '-=0.35')
        .to('#bowl', { y: 0, opacity: 1, duration: 0.45, ease: 'back.out(1.5)' }, '-=0.35')
        .to(['#leaf-big', '#leaf-small'], { scale: 1, duration: 0.5, ease: 'elastic.out(1, 0.4)', stagger: 0 }, '-=0.3')
        
        .to('#cloche-arc', { strokeDashoffset: 0, duration: 0.45, ease: 'back.out(1.2)' }, '-=0.35')
        .to('#cloche-handle', { scale: 1, opacity: 1, duration: 0.35, ease: 'elastic.out(1, 0.45)' }, '-=0.3')
        .to('#ecg-base', { strokeDashoffset: 0, duration: 0.3, ease: 'power2.inOut' }, '-=0.35')
        .to('#ecg-line', { strokeDashoffset: 0, duration: 0.6, ease: 'power2.inOut' }, '-=0.35')
        .to('#ecg-dot', { scale: 1, opacity: 1, duration: 0.35, ease: 'elastic.out(1, 0.4)' }, '-=0.25')
        
        .to('.steam-path', { strokeDashoffset: 0, duration: 0.5, ease: 'elastic.out(1, 0.5)', stagger: 0 }, '-=0.25')
        
        .to(['#text-pantry', '#text-pulse'], { opacity: 1, duration: 0.5, ease: 'elastic.out(1, 0.4)' }, '-=0.3')
        .to('#text-leaf', { scale: 1, duration: 0.45, ease: 'elastic.out(1, 0.3)' }, '-=0.3')
        
        .to('#tagline-lines', { strokeDashoffset: 0, duration: 0.3, ease: 'back.out(1.2)' }, '-=0.3');

      const typingObj = { val: 0 };
      tl.to(typingObj, {
        val: tagline.length,
        duration: 0.9,
        ease: 'none',
        onUpdate: () => {
          const charCount = Math.floor(typingObj.val);
          const tag1 = document.getElementById('tag-1');
          if (tag1) tag1.innerHTML = tagline.substring(0, charCount);
        }
      }, '-=0.25');

      tl.to('#cutlery', { scale: 0.6, opacity: 1, duration: 0.4, ease: 'elastic.out(1, 0.3)' }, '-=0.2')
        .to('.logo-svg', { scale: 1.03, duration: 0.35, ease: 'power2.out' }, '-=0.2')
        .to('.logo-svg', { scale: 1, duration: 0.3, ease: 'power2.in' });

      tl.to(this.energyBlast.nativeElement, {
        width: '300vw',
        height: '300vw',
        opacity: 1,
        duration: 0.8,
        ease: 'power2.inOut'
      }, '+=0.1')
      .to('.splash-container', { opacity: 0, duration: 0.4 }, '-=0.2');

    } else {
      // 3. GOLD Theme - Premium Coordinating Sequential reveal
      // Step 1: The complete shelf/frame appears together
      tl.to('#shelf path', { strokeDashoffset: 0, duration: 0.4, ease: 'power2.out', stagger: 0 })
        
        // Step 2: The three jars animate into place together
        .to(['#jar-1', '#jar-2', '#jar-3'], { y: 0, opacity: 1, duration: 0.4, ease: 'back.out(1.2)', stagger: 0 }, '-=0.3')
        
        // Step 3: The bowl and leaf appear together
        .to('#bowl', { y: 0, opacity: 1, duration: 0.4, ease: 'back.out(1.2)' }, '-=0.3')
        .to(['#leaf-big', '#leaf-small'], { scale: 1, duration: 0.4, ease: 'elastic.out(1, 0.4)', stagger: 0 }, '-=0.3')
        
        // Step 4: The serving dome and heartbeat line animate together
        .to('#cloche-arc', { strokeDashoffset: 0, duration: 0.4, ease: 'power2.inOut' }, '-=0.3')
        .to('#cloche-handle', { scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)' }, '-=0.3')
        .to('#ecg-base', { strokeDashoffset: 0, duration: 0.25, ease: 'power2.out' }, '-=0.3')
        .to('#ecg-line', { strokeDashoffset: 0, duration: 0.5, ease: 'power2.inOut' }, '-=0.3')
        .to('#ecg-dot', { scale: 1, opacity: 1, duration: 0.25, ease: 'back.out(2)' }, '-=0.2')
        
        // Step 5: The steam appears
        .to('.steam-path', { strokeDashoffset: 0, duration: 0.4, ease: 'power1.inOut', stagger: 0 }, '-=0.3')
        
        // Step 6: The entire "PantryPulse" text fades in together (no letter-by-letter reveal)
        .to(['#text-pantry', '#text-pulse'], { opacity: 1, duration: 0.4, ease: 'power2.out' }, '-=0.3')
        .to('#text-leaf', { scale: 1, duration: 0.35, ease: 'elastic.out(1, 0.4)' }, '-=0.3')
        
        // Step 7: The tagline appears
        .to('#tagline-lines', { strokeDashoffset: 0, duration: 0.25 }, '-=0.25');

      const typingObj = { val: 0 };
      tl.to(typingObj, {
        val: tagline.length,
        duration: 0.8,
        ease: 'none',
        onUpdate: () => {
          const charCount = Math.floor(typingObj.val);
          const tag1 = document.getElementById('tag-1');
          if (tag1) tag1.innerHTML = tagline.substring(0, charCount);
        }
      }, '-=0.2');

      // Step 8: The fork-and-spoon icon appears with a subtle fade and scale
      tl.to('#cutlery', { scale: 0.6, opacity: 1, duration: 0.4, ease: 'back.out(1.5)' }, '-=0.2')
        .to('.logo-svg', { filter: 'drop-shadow(0 0 20px rgba(224, 194, 148, 0.4))', duration: 0.5 }, '-=0.2')
        .to('.particles', { scale: 1.03, duration: 0.5 }, '-=0.5');

      tl.to(this.energyBlast.nativeElement, {
        width: '300vw',
        height: '300vw',
        opacity: 1,
        duration: 0.8,
        ease: 'power3.in'
      }, '+=0.05')
      .to('.splash-container', { opacity: 0, duration: 0.3 }, '-=0.15');
    }
  }

  private navigateToApp(): void {
    this.router.navigate(['/login']);
  }
}
